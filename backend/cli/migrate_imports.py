#!/usr/bin/env python3
"""
Script to migrate imports from old paths to new paths.
Run this script once after restructuring.
"""
import os
import re

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Models
    "from backend.models import": "from backend.models import",
    "from backend.models import User": "from backend.models.user import User",
    "from backend.models import User,": "from backend.models.user import User,",
    "from backend.models import Project": "from backend.models.project import Project",
    "from backend.models import Project,": "from backend.models.project import Project,",
    "from backend.models import SysModel": "from backend.models.system import SysModel",
    "from backend.models import SysModel,": "from backend.models.system import SysModel,",
    "from backend.models import SysField": "from backend.models.system import SysField",
    "from backend.models import SysField,": "from backend.models.system import SysField,",
    "from backend.models import Product": "from backend.models.product import Product",
    "from backend.models import Product,": "from backend.models.product import Product,",
    "from backend.models import SalesOrder": "from backend.models.sales import SalesOrder",
    "from backend.models import SalesOrder,": "from backend.models.sales import SalesOrder,",
    "from backend.models import PurchaseOrder": "from backend.models.purchase import PurchaseOrder",
    "from backend.models import PurchaseOrder,": "from backend.models.purchase import PurchaseOrder,",
    "from backend.models import AIConversation": "from backend.models.ai import AIConversation",
    "from backend.models import ChartLibraryConfig": "from backend.models.chart import ChartLibraryConfig",
    "from backend.models import SysView": "from backend.models.system import SysView",
    "from backend.models import SysView,": "from backend.models.system import SysView,",
    "from backend.models import SysComponent": "from backend.models.system import SysComponent",
    "from backend.models import SysComponent,": "from backend.models.system import SysComponent,",
    "from backend.models import SysAction": "from backend.models.system import SysAction",
    "from backend.models import SysAction,": "from backend.models.system import SysAction,",
    "from backend.models import SysChart": "from backend.models.system import SysChart",
    "from backend.models import SysDashboard": "from backend.models.system import SysDashboard",
    "from backend.models import SysModelVersion": "from backend.models.system import SysModelVersion",
    
    # API routes - these will be updated to new paths
    "from backend.projects import": "from backend.endpoints.projects import",
    "from backend.dashboard import": "from backend.endpoints.dashboard import",
    "from backend.analytics import": "from backend.endpoints.analytics import",
    "from backend.dynamic_api import": "from backend.endpoints.dynamic import",
    "from backend.template_api import": "from backend.endpoints.templates import",
    "from backend.visual_builder_api import": "from backend.endpoints.visual_builder import",
    "from backend.versioning_api import": "from backend.endpoints.versioning import",
    "from backend.debugging_api import": "from backend.endpoints.debugging import",
    "from backend.gdo_reconciliation_api import": "from backend.endpoints.gdo import",
    
    # Workflow & Webhook
    "from backend.workflows import": "from backend.models.workflow import",
    "from backend.webhooks import": "from backend.models.webhook import",
    
    # Services
    "from backend.workflow_service import": "from backend.services.workflow_service import",
    "from backend.webhook_service import": "from backend.services.webhook_service import",
}

def process_file(filepath):
    """Process a single file and update imports."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        for old, new in IMPORT_MAPPINGS.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    backend_dir = "backend"
    count = 0
    
    for root, dirs, files in os.walk(backend_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                if process_file(filepath):
                    print(f"Updated: {filepath}")
                    count += 1
    
    print(f"\nTotal files updated: {count}")

if __name__ == "__main__":
    main()
