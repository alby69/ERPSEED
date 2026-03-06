"""
Webhook Routes.

API endpoints for webhook management.
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

import json
from datetime import datetime
from .webhooks import WebhookEndpoint, WebhookDelivery, WebhookEvent
from .webhook_service import WebhookService
from .extensions import db

blp = Blueprint("webhooks", __name__, url_prefix="/webhooks", description="Webhook Management")

class WebhookEndpointSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    events = fields.List(fields.Str(), required=True)
    is_active = fields.Bool()
    created_at = fields.Str(dump_only=True, allow_none=True)

class WebhookEndpointDetailSchema(WebhookEndpointSchema):
    secret = fields.Str(dump_only=True)

class WebhookDeliverySchema(Schema):
    id = fields.Int(dump_only=True)
    endpoint_id = fields.Int()
    event = fields.Str()
    status_code = fields.Int(allow_none=True)
    attempts = fields.Int()
    delivered_at = fields.Str(allow_none=True)
    error = fields.Str(dump_only=True, attribute="error_message", allow_none=True)
    is_success = fields.Bool(dump_only=True)

class WebhookTestResponseSchema(Schema):
    success = fields.Bool()
    status_code = fields.Int(allow_none=True)
    response = fields.Str(allow_none=True)
    error = fields.Str(allow_none=True)

class WebhookSecretSchema(Schema):
    secret = fields.Str()

class WebhookEventListSchema(Schema):
    events = fields.List(fields.Str())
    categories = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))


@blp.route("")
class WebhookList(MethodView):
    """Webhook endpoint management."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookEndpointSchema(many=True))
    def get(self):
        """List all webhook endpoints."""
        endpoints = WebhookEndpoint.query.order_by(WebhookEndpoint.created_at.desc()).all()
        result = []
        for ep in endpoints:
            result.append({
                'id': ep.id,
                'name': ep.name,
                'url': ep.url,
                'events': ep.get_events(),
                'is_active': ep.is_active,
                'created_at': ep.created_at.isoformat() if ep.created_at else None
            })
        return result
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(WebhookEndpointSchema)
    @blp.response(201, WebhookEndpointDetailSchema)
    def post(self, data):
        """Create a new webhook endpoint."""
        
        # Validate events
        all_events = WebhookEvent.get_all_events()
        for event in data['events']:
            if event != WebhookEvent.ALL and event not in all_events:
                abort(400, message=f"Invalid event: {event}")
        
        user_id = get_jwt_identity()
        
        endpoint = WebhookService.create_endpoint(
            name=data['name'],
            url=data['url'],
            events=data['events'],
            user_id=user_id
        )
        
        return endpoint


@blp.route("/<int:endpoint_id>")
class WebhookResource(MethodView):
    """Single webhook endpoint."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookEndpointSchema)
    def get(self, endpoint_id):
        """Get webhook endpoint details (secret hidden)."""
        endpoint = WebhookEndpoint.query.get_or_404(endpoint_id)
        
        return {
            'id': endpoint.id,
            'name': endpoint.name,
            'url': endpoint.url,
            'events': endpoint.get_events(),
            'is_active': endpoint.is_active,
            'created_at': endpoint.created_at.isoformat() if endpoint.created_at else None
        }
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(WebhookEndpointSchema(partial=True))
    @blp.response(200, WebhookEndpointSchema)
    def put(self, data, endpoint_id):
        """Update webhook endpoint."""
        
        if 'events' in data:
            all_events = WebhookEvent.get_all_events()
            for event in data['events']:
                if event != WebhookEvent.ALL and event not in all_events:
                    abort(400, message=f"Invalid event: {event}")
        
        endpoint = WebhookService.update_endpoint(endpoint_id, data)
        
        return endpoint
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, endpoint_id):
        """Delete webhook endpoint."""
        WebhookService.delete_endpoint(endpoint_id)
        return ''


@blp.route("/<int:endpoint_id>/test")
class WebhookTest(MethodView):
    """Test webhook endpoint."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookTestResponseSchema)
    def post(self, endpoint_id):
        """Send test webhook."""
        endpoint = WebhookEndpoint.query.get_or_404(endpoint_id)
        
        test_payload = {
            'event': 'test',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': {
                'message': 'This is a test webhook from FlaskERP',
                'endpoint_id': endpoint_id
            }
        }
        
        delivery = WebhookService._deliver_webhook(endpoint, 'test', test_payload)
        
        return {
            'success': delivery.is_success,
            'status_code': delivery.status_code,
            'response': delivery.response_body[:200] if delivery.response_body else None,
            'error': delivery.error_message
        }


@blp.route("/<int:endpoint_id>/regenerate-secret")
class WebhookRegenerateSecret(MethodView):
    """Regenerate webhook secret."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookSecretSchema)
    def post(self, endpoint_id):
        """Regenerate webhook secret."""
        secret = WebhookService.regenerate_secret(endpoint_id)
        
        return {'secret': secret}


@blp.route("/deliveries")
class WebhookDeliveries(MethodView):
    """Webhook delivery history."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookDeliverySchema(many=True))
    def get(self):
        """List webhook deliveries."""
        endpoint_id = request.args.get('endpoint_id', type=int)
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        deliveries = WebhookService.get_deliveries(
            endpoint_id=endpoint_id if endpoint_id else 0,
            status=status if status else "",
            limit=limit
        )
        
        return deliveries


@blp.route("/events")
class WebhookEvents(MethodView):
    """Available webhook events."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookEventListSchema)
    def get(self):
        """Get list of available webhook events."""
        return WebhookEvent.get_event_map()


@blp.route("/deliveries/<int:delivery_id>/retry")
class WebhookRetry(MethodView):
    """Retry failed delivery."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WebhookTestResponseSchema)
    def post(self, delivery_id):
        """Retry a failed webhook delivery."""
        delivery = WebhookDelivery.query.get_or_404(delivery_id)
        
        if delivery.is_success:
            abort(400, message="Delivery already succeeded")
        
        endpoint = delivery.endpoint
        if not endpoint or not endpoint.is_active:
            abort(400, message="Endpoint is not active")
        
        payload = {
            'event': delivery.event,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': json.loads(delivery.payload)['data'] if delivery.payload else {} # type: ignore
        }
        
        new_delivery = WebhookService._deliver_webhook(endpoint, delivery.event, payload)
        
        return {
            'success': new_delivery.is_success,
            'status_code': new_delivery.status_code
        }
