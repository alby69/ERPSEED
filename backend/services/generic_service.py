from flask_smorest import abort
from backend.extensions import db
from typing import Optional, List


class GenericService:
    @staticmethod
    def create_scoped_resource(model, data, scope_filters: dict, unique_fields: Optional[List] = None, commit=True):
        """
        Generic function to create a resource within a specific scope (e.g., tenant, project).
        Accepts either a dictionary or a model instance.
        """
        if isinstance(data, dict):
            resource = model(**data)
        else:
            resource = data

        # Apply scope
        for key, value in scope_filters.items():
            setattr(resource, key, value)

        if unique_fields:
            filter_args = scope_filters.copy()
            is_valid_check = True
            for field in unique_fields:
                value = getattr(resource, field, None)
                if value is None:
                    # Cannot check uniqueness if part of the key is null.
                    is_valid_check = False
                    break
                filter_args[field] = value

            if is_valid_check:
                existing = model.query.filter_by(**filter_args).first()
                if existing:
                    field_names = ", ".join(unique_fields)
                    abort(409, message=f"A record with these values for ({field_names}) already exists.")

        db.session.add(resource)
        if commit:
            db.session.commit()
        return resource

    @staticmethod
    def create_tenant_resource(model, data, tenant_id, unique_fields: Optional[List] = None, commit=True):
        """
        Generic function to create a tenant-scoped resource.
        Accepts either a dictionary or a model instance.
        """
        return GenericService.create_scoped_resource(
            model, data, {'tenant_id': tenant_id}, unique_fields, commit
        )

    @staticmethod
    def create_resource(model, data, commit=True):
        """Generic function to create a non-tenant-scoped resource."""
        if isinstance(data, dict):
            resource = model(**data)
        else:
            resource = data

        db.session.add(resource)
        if commit:
            db.session.commit()
        return resource

    @staticmethod
    def get_tenant_resource(model, resource_id, tenant_id, not_found_message="Resource not found"):
        """Generic function to get a tenant-scoped resource."""
        resource = model.query.filter_by(id=resource_id, tenant_id=tenant_id).first()
        if not resource:
            abort(404, message=not_found_message)
        return resource

    @staticmethod
    def get_resource(model, resource_id, not_found_message="Resource not found"):
        """Generic function to get a non-tenant-scoped resource."""
        resource = model.query.get_or_404(resource_id, description=not_found_message)
        return resource

    @staticmethod
    def update_tenant_resource(model, resource_id, tenant_id, data, not_found_message="Resource not found"):
        """Generic function to update a tenant-scoped resource."""
        resource = model.query.filter_by(id=resource_id, tenant_id=tenant_id).first()
        if not resource:
            abort(404, message=not_found_message)

        for key, value in data.items():
            # Prevent updating primary key or tenant_id
            if key in ['id', 'tenant_id']:
                continue
            if hasattr(resource, key):
                setattr(resource, key, value)

        db.session.commit()
        return resource

    @staticmethod
    def update_resource(model, resource_id, data, not_found_message="Resource not found"):
        """Generic function to update a non-tenant-scoped resource."""
        resource = model.query.get_or_404(resource_id, description=not_found_message)

        for key, value in data.items():
            if key == 'id':
                continue
            if hasattr(resource, key):
                setattr(resource, key, value)

        db.session.commit()
        return resource

    @staticmethod
    def delete_tenant_resource(model, resource_id, tenant_id, pre_delete_check=None, not_found_message="Resource not found"):
        """
        Generic function to delete a tenant-scoped resource with an optional pre-delete check.

        :param model: The SQLAlchemy model class.
        :param resource_id: The ID of the resource to delete.
        :param tenant_id: The ID of the current tenant.
        :param pre_delete_check: A function that takes the resource instance and performs checks.
                                 It should call abort() if deletion is not allowed.
        :param not_found_message: Custom 404 message.
        """
        resource = model.query.filter_by(id=resource_id, tenant_id=tenant_id).first()
        if not resource:
            abort(404, message=not_found_message)

        if pre_delete_check:
            pre_delete_check(resource)

        db.session.delete(resource)
        db.session.commit()

    @staticmethod
    def delete_resource(model, resource_id, pre_delete_check=None, not_found_message="Resource not found"):
        """
        Generic function to delete a non-tenant-scoped resource with an optional pre-delete check.

        :param model: The SQLAlchemy model class.
        :param resource_id: The ID of the resource to delete.
        :param pre_delete_check: A function that takes the resource instance and performs checks.
        :param not_found_message: Custom 404 message.
        """
        resource = model.query.get_or_404(resource_id, description=not_found_message)

        if pre_delete_check:
            pre_delete_check(resource)

        db.session.delete(resource)
        db.session.commit()

generic_service = GenericService()