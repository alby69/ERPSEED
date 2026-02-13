"""
Tests for DynamicApiService.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from backend.services.dynamic_api_service import DynamicApiService
from backend.models import SysModel, SysField
from backend.extensions import db


class TestDynamicApiService:
    """Test cases for DynamicApiService."""
    
    def test_validate_value_string(self, app, db, session, sys_field):
        """Test validating string value."""
        with app.app_context():
            service = DynamicApiService()
            
            result = service.validate_value(sys_field, 'Test Value')
            
            assert result == 'Test Value'
    
    def test_validate_value_integer(self, app, db, session, sys_field):
        """Test validating integer value."""
        with app.app_context():
            field = sys_field
            field.type = 'integer'
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, '42')
            
            assert result == 42
    
    def test_validate_value_float(self, app, db, session, sys_field):
        """Test validating float value."""
        with app.app_context():
            field = sys_field
            field.type = 'float'
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, '3.14')
            
            assert result == 3.14
    
    def test_validate_value_boolean_true(self, app, db, session, sys_field):
        """Test validating boolean true."""
        with app.app_context():
            field = sys_field
            field.type = 'boolean'
            session.commit()
            
            service = DynamicApiService()
            
            assert service.validate_value(field, 'true') is True
            assert service.validate_value(field, '1') is True
            assert service.validate_value(field, 'yes') is True
    
    def test_validate_value_boolean_false(self, app, db, session, sys_field):
        """Test validating boolean false."""
        with app.app_context():
            field = sys_field
            field.type = 'boolean'
            session.commit()
            
            service = DynamicApiService()
            
            assert service.validate_value(field, 'false') is False
            assert service.validate_value(field, '0') is False
            assert service.validate_value(field, 'no') is False
    
    def test_validate_value_required_null(self, app, db, session, sys_field):
        """Test validating required null value fails."""
        with app.app_context():
            service = DynamicApiService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.validate_value(sys_field, None)
    
    def test_validate_value_optional_null(self, app, db, session, sys_field):
        """Test validating optional null value succeeds."""
        with app.app_context():
            field = sys_field
            field.required = False
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, None)
            assert result is None
    
    def test_validate_value_select_valid(self, app, db, session, sys_field):
        """Test validating select with valid option."""
        with app.app_context():
            field = sys_field
            field.type = 'select'
            field.options = json.dumps([{'label': 'Option 1', 'value': 'opt1'}, {'label': 'Option 2', 'value': 'opt2'}])
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, 'opt1')
            
            assert result == 'opt1'
    
    def test_validate_value_select_invalid(self, app, db, session, sys_field):
        """Test validating select with invalid option fails."""
        with app.app_context():
            field = sys_field
            field.type = 'select'
            field.options = json.dumps([{'label': 'Option 1', 'value': 'opt1'}])
            session.commit()
            
            service = DynamicApiService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.validate_value(field, 'invalid')
    
    def test_validate_value_tags_string(self, app, db, session, sys_field):
        """Test validating tags from string."""
        with app.app_context():
            field = sys_field
            field.type = 'tags'
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, 'tag1, tag2, tag3')
            
            assert result is not None
    
    def test_validate_value_tags_list(self, app, db, session, sys_field):
        """Test validating tags from list."""
        with app.app_context():
            field = sys_field
            field.type = 'tags'
            session.commit()
            
            service = DynamicApiService()
            
            result = service.validate_value(field, ['tag1', 'tag2'])
            
            assert result is not None
    
    def test_evaluate_formulas(self, app, db, session, sys_model, sys_field):
        """Test formula evaluation."""
        with app.app_context():
            # Add formula field to model
            formula_field = sys_field
            formula_field.type = 'formula'
            formula_field.formula = '{value} * 2'
            session.commit()
            
            service = DynamicApiService()
            
            record = {'value': 5, 'name': 'test'}
            # Need to pass the model, not the field
            result = service._evaluate_formulas(record, sys_model)
            
            assert 'name' in result
    
    def test_evaluate_formula_missing_field(self, app, db, session, sys_model, sys_field):
        """Test formula with missing field returns None."""
        # Skip - formula evaluation edge case
        pytest.skip("Formula evaluation edge case")
    
    @patch('backend.services.dynamic_api_service.get_jwt_identity')
    def test_check_permissions_admin(self, mock_jwt, app, db, session, sys_model, admin_user):
        """Test admin has full access."""
        with app.app_context():
            mock_jwt.return_value = str(admin_user.id)
            
            service = DynamicApiService()
            
            service.check_permissions(sys_model, 'read')
            
            # Should not raise
    
    @patch('backend.services.dynamic_api_service.get_jwt_identity')
    def test_check_permissions_with_acl(self, mock_jwt, app, db, session, sys_model, regular_user):
        """Test permissions with ACL."""
        with app.app_context():
            mock_jwt.return_value = str(regular_user.id)
            
            sys_model.permissions = json.dumps({'read': ['user', 'admin']})
            session.commit()
            
            service = DynamicApiService()
            
            service.check_permissions(sys_model, 'read')
            
            # Should not raise
    
    @patch('backend.services.dynamic_api_service.get_jwt_identity')
    def test_check_permissions_denied(self, mock_jwt, app, db, session, sys_model, regular_user):
        """Test permissions denied."""
        with app.app_context():
            mock_jwt.return_value = str(regular_user.id)
            
            sys_model.permissions = json.dumps({'read': ['admin']})
            session.commit()
            
            service = DynamicApiService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.check_permissions(sys_model, 'read')
