"""
Tests for BuilderService.
"""
import pytest
from backend.services.builder_service import BuilderService
from backend.models import SysModel, SysField
from backend.extensions import db


class TestBuilderService:
    """Test cases for BuilderService."""
    
    def test_get_all_models(self, app, db, session, project, sys_model):
        """Test getting all models."""
        with app.app_context():
            service = BuilderService()
            
            models, headers = service.get_all_models(search_fields=['name', 'title'])
            
            assert len(models) >= 1
    
    def test_get_model(self, app, db, session, sys_model):
        """Test getting single model."""
        with app.app_context():
            service = BuilderService()
            
            model = service.get_model(sys_model.id)
            
            assert model is not None
            assert model.name == 'customers'
    
    def test_create_model(self, app, db, session, project):
        """Test creating a new model."""
        with app.app_context():
            service = BuilderService()
            
            model = service.create_model(
                project_id=project.id,
                name='orders',
                title='Orders',
                description='Order records'
            )
            
            assert model is not None
            assert model.name == 'orders'
            assert model.title == 'Orders'
            assert model.project_id == project.id
    
    def test_create_duplicate_model_fails(self, app, db, session, project, sys_model):
        """Test creating duplicate model fails."""
        with app.app_context():
            service = BuilderService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.create_model(
                    project_id=project.id,
                    name='customers',
                    title='Duplicate'
                )
    
    def test_update_model(self, app, db, session, sys_model):
        """Test updating a model."""
        with app.app_context():
            service = BuilderService()
            
            updated = service.update_model(
                sys_model.id,
                {'title': 'Updated Customers', 'description': 'New description'}
            )
            
            assert updated.title == 'Updated Customers'
            assert updated.description == 'New description'
    
    def test_update_model_duplicate_name_fails(self, app, db, session, project, sys_model):
        """Test updating to duplicate name fails."""
        with app.app_context():
            service = BuilderService()
            
            new_model = service.create_model(
                project_id=project.id,
                name='orders',
                title='Orders'
            )
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.update_model(
                    new_model.id,
                    {'name': 'customers'}
                )
    
    def test_delete_model(self, app, db, session, sys_model):
        """Test deleting a model."""
        with app.app_context():
            service = BuilderService()
            
            model_id = sys_model.id
            service.delete_model(model_id)
            
            model = service.get_model(model_id)
            assert model is None
    
    def test_create_field(self, app, db, session, sys_model):
        """Test creating a field."""
        with app.app_context():
            service = BuilderService()
            
            field = service.create_field(
                model_id=sys_model.id,
                name='email',
                field_type='string',
                title='Email Address',
                required=True
            )
            
            assert field is not None
            assert field.name == 'email'
            assert field.type == 'string'
            assert field.required is True
    
    def test_create_duplicate_field_fails(self, app, db, session, sys_field):
        """Test creating duplicate field fails."""
        with app.app_context():
            service = BuilderService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.create_field(
                    model_id=sys_field.model_id,
                    name='name',
                    field_type='string'
                )
    
    def test_update_field(self, app, db, session, sys_field):
        """Test updating a field."""
        with app.app_context():
            service = BuilderService()
            
            updated = service.update_field(
                sys_field.id,
                {'title': 'Full Name', 'required': False}
            )
            
            assert updated.title == 'Full Name'
            assert updated.required is False
    
    def test_delete_field(self, app, db, session, sys_field):
        """Test deleting a field."""
        with app.app_context():
            service = BuilderService()
            
            field_id = sys_field.id
            service.delete_field(field_id)
            
            from backend.models import SysField
            field = db.session.get(SysField, field_id)
            assert field is None
    
    def test_clone_model(self, app, db, session, project, sys_model, sys_field):
        """Test cloning a model."""
        with app.app_context():
            service = BuilderService()
            
            cloned = service.clone_model(
                model_id=sys_model.id,
                user_id=project.owner_id,
                new_name='customers_backup',
                new_title='Customers Backup'
            )
            
            assert cloned is not None
            assert cloned.name == 'customers_backup'
            assert cloned.title == 'Customers Backup'
            assert cloned.id != sys_model.id
            
            assert len(list(cloned.fields)) >= 1
    
    def test_clone_duplicate_name_fails(self, app, db, session, project, sys_model):
        """Test cloning to duplicate name fails."""
        with app.app_context():
            service = BuilderService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.clone_model(
                    model_id=sys_model.id,
                    user_id=project.owner_id,
                    new_name='customers',
                    new_title='Duplicate'
                )
    
    def test_get_audit_logs(self, app, db, session):
        """Test getting audit logs."""
        with app.app_context():
            service = BuilderService()
            
            logs, total = service.get_audit_logs(page=1, per_page=10)
            
            assert isinstance(logs, list)
            assert isinstance(total, int)
    
    def test_model_with_all_field_types(self, app, db, session, project):
        """Test creating model with various field types."""
        with app.app_context():
            service = BuilderService()
            
            model = service.create_model(
                project_id=project.id,
                name='complex_model',
                title='Complex Model'
            )
            
            field_types = ['string', 'text', 'integer', 'float', 'boolean', 'date', 'datetime', 'select']
            
            for field_type in field_types:
                field = service.create_field(
                    model_id=model.id,
                    name=f'field_{field_type}',
                    field_type=field_type,
                    title=f'Field {field_type}'
                )
                assert field is not None
                assert field.type == field_type
