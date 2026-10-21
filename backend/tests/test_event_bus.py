"""
Tests for Core EventBus and decoupled event dispatching.
"""
import pytest
from backend.core.event_bus import EventBus, DomainEvent, get_event_bus
from backend.modules.sales.listeners import register_sales_event_listeners, InventoryListener, InvoicingListener


def test_core_event_bus_publish_subscribe():
    bus = EventBus()
    received = []

    def sample_handler(event: DomainEvent):
        received.append(event.payload)

    bus.subscribe("order.confirmed", sample_handler)
    test_event = DomainEvent(event_type="order.confirmed", payload={"order_id": 101, "customer_id": 45})
    bus.publish(test_event)

    assert len(received) == 1
    assert received[0]["order_id"] == 101


def test_sales_event_listeners_integration():
    bus = EventBus()
    logs = []

    class MockInventoryListener:
        def __call__(self, event: DomainEvent):
            logs.append(f"inventory:{event.event_type}:{event.payload.get('order_id')}")

    class MockInvoicingListener:
        def __call__(self, event: DomainEvent):
            logs.append(f"invoicing:{event.event_type}:{event.payload.get('order_id')}")

    bus.subscribe("sales_order.confirmed", MockInventoryListener())
    bus.subscribe("order.confirmed", MockInventoryListener())
    bus.subscribe("sales_order.confirmed", MockInvoicingListener())
    bus.subscribe("order.confirmed", MockInvoicingListener())

    event1 = DomainEvent(event_type="sales_order.confirmed", payload={"order_id": 200, "tenant_id": 1})
    event2 = DomainEvent(event_type="order.confirmed", payload={"order_id": 201, "tenant_id": 1})

    bus.publish(event1)
    bus.publish(event2)

    assert "inventory:sales_order.confirmed:200" in logs
    assert "invoicing:sales_order.confirmed:200" in logs
    assert "inventory:order.confirmed:201" in logs
    assert "invoicing:order.confirmed:201" in logs
