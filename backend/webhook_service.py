"""
Webhook Service.

Handles webhook triggering, retries, and delivery.
"""
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app
from sqlalchemy import desc

from .webhooks import WebhookEndpoint, WebhookDelivery, WebhookEvent


class WebhookService:
    """
    Service for managing webhooks.
    Handles event triggering, delivery, and retries.
    """
    
    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min
    
    @staticmethod
    def trigger_event(event: str, data: Dict[str, Any], async_mode: bool = True):
        """
        Trigger a webhook event to all matching endpoints.
        
        Args:
            event: Event type (e.g., 'user.created')
            data: Event payload data
            async_mode: If True, deliver in background using Celery/threading
        """
        endpoints = WebhookEndpoint.query.filter_by(is_active=True).all()
        
        matching_endpoints = []
        for endpoint in endpoints:
            endpoint_events = endpoint.get_events()
            if WebhookEvent.ALL in endpoint_events or event in endpoint_events:
                matching_endpoints.append(endpoint)
        
        if not matching_endpoints:
            return
        
        payload = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': data
        }
        
        if async_mode:
            for endpoint in matching_endpoints:
                WebhookService._deliver_webhook(endpoint, event, payload)
        else:
            for endpoint in matching_endpoints:
                WebhookService._deliver_webhook(endpoint, event, payload)
    
    @staticmethod
    def _deliver_webhook(endpoint: WebhookEndpoint, event: str, payload: dict):
        """
        Deliver webhook to a single endpoint.
        
        Args:
            endpoint: WebhookEndpoint instance
            event: Event type
            payload: Full payload to send
        """
        import sys
        
        payload_str = json.dumps(payload, default=str)
        signature = endpoint.sign_payload(payload_str)
        
        delivery = WebhookDelivery()
        delivery.endpoint_id=endpoint.id
        delivery.event=event
        delivery.payload=payload_str
        from backend.extensions import db
        db.session.add(delivery)
        db.session.flush()
        
        try:
            response = requests.post(
                endpoint.url,
                data=payload_str,
                headers={
                    'Content-Type': 'application/json',
                    'X-Webhook-Signature': signature,
                    'X-Webhook-Event': event,
                    'User-Agent': 'FlaskERP-Webhook/1.0'
                },
                timeout=30,
                verify=True
            )
            
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000] if response.text else None
            delivery.delivered_at = datetime.utcnow()
            delivery.attempts += 1
            
            if 200 <= response.status_code < 300:
                pass  # Success
            elif delivery.attempts < WebhookService.MAX_RETRIES:
                delay = WebhookService.RETRY_DELAYS[delivery.attempts - 1]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
            else:
                delivery.error_message = f"Failed after {delivery.attempts} attempts"
        
        except requests.exceptions.Timeout:
            delivery.error_message = "Request timeout"
            delivery.status_code = 0
            delivery.attempts += 1
            if delivery.attempts < WebhookService.MAX_RETRIES:
                delay = WebhookService.RETRY_DELAYS[delivery.attempts - 1]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
                
        except requests.exceptions.RequestException as e:
            delivery.error_message = str(e)
            delivery.status_code = 0
            delivery.attempts += 1
            if delivery.attempts < WebhookService.MAX_RETRIES:
                delay = WebhookService.RETRY_DELAYS[delivery.attempts - 1]
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
        
        except Exception as e:
            delivery.error_message = f"Unexpected error: {str(e)}"
            delivery.status_code = 0
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        db.session.commit()
        
        return delivery
    
    @staticmethod
    def retry_failed_deliveries():
        """Retry failed webhook deliveries."""
        pending = WebhookDelivery.query.filter(
            WebhookDelivery.next_retry_at <= datetime.utcnow(),
            WebhookDelivery.attempts < WebhookService.MAX_RETRIES
        ).order_by(desc(WebhookDelivery.created_at)).limit(100).all()
        
        for delivery in pending:
            endpoint = delivery.endpoint
            if endpoint and endpoint.is_active:
                payload = json.loads(delivery.payload)
                WebhookService._deliver_webhook(endpoint, delivery.event, payload)
    
    @staticmethod
    def create_endpoint(name: str, url: str, events: list, user_id: int) -> WebhookEndpoint:
        """Create a new webhook endpoint."""
        from backend.extensions import db
        
        endpoint = WebhookEndpoint()
        endpoint.name=name
        endpoint.url=url
        endpoint.secret=WebhookEndpoint.generate_secret()
        endpoint.events=json.dumps(events)
        endpoint.created_by=user_id
        
        db.session.add(endpoint)
        db.session.commit()
        
        return endpoint
    
    @staticmethod
    def update_endpoint(endpoint_id: int, data: dict) -> WebhookEndpoint:
        """Update a webhook endpoint."""
        from backend.extensions import db
        
        endpoint = db.session.get(WebhookEndpoint, endpoint_id)
        if not endpoint:
            raise ValueError(f"Webhook endpoint {endpoint_id} not found")
        
        if 'name' in data:
            endpoint.name = data['name']
        if 'url' in data:
            endpoint.url = data['url']
        if 'events' in data:
            endpoint.set_events(data['events'])
        if 'is_active' in data:
            endpoint.is_active = data['is_active']
        
        db.session.commit()
        return endpoint
    
    @staticmethod
    def delete_endpoint(endpoint_id: int):
        """Delete a webhook endpoint."""
        from backend.extensions import db
        
        endpoint = db.session.get(WebhookEndpoint, endpoint_id)
        if endpoint:
            db.session.delete(endpoint)
            db.session.commit()
    
    @staticmethod
    def get_deliveries_query(endpoint_id: Optional[int] = None, status: Optional[str] = None):
        """Get webhook deliveries query with filters."""
        query = WebhookDelivery.query
        
        if endpoint_id:
            query = query.filter_by(endpoint_id=endpoint_id)
        
        if status == 'success':
            query = query.filter(WebhookDelivery.status_code >= 200, WebhookDelivery.status_code < 300)
        elif status == 'failed':
            query = query.filter(
                (WebhookDelivery.status_code >= 400) | 
                (WebhookDelivery.status_code == 0)
            )
        elif status == 'pending':
            query = query.filter(WebhookDelivery.next_retry_at > datetime.utcnow())
        
        return query.order_by(desc(WebhookDelivery.created_at))
    
    @staticmethod
    def regenerate_secret(endpoint_id: int) -> str:
        """Regenerate webhook secret."""
        from backend.extensions import db
        
        endpoint = db.session.get(WebhookEndpoint, endpoint_id)
        if not endpoint:
            raise ValueError(f"Webhook endpoint {endpoint_id} not found")
        
        endpoint.secret = WebhookEndpoint.generate_secret()
        db.session.commit()
        
        return endpoint.secret


# Helper function to trigger webhooks easily
def trigger_webhook(event: str, data: Dict[str, Any], async_mode: bool = True):
    """
    Convenience function to trigger a webhook event.
    
    Usage:
        trigger_webhook('user.created', {'user_id': 1, 'email': 'test@example.com'})
    """
    try:
        WebhookService.trigger_event(event, data, async_mode)
    except Exception as e:
        import traceback
        print(f"Webhook trigger failed: {e}", file=traceback.print_exc())
