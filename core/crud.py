import os
import csv
import io
from werkzeug.utils import secure_filename
from flask import request, current_app, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, func, inspect
from sqlalchemy.orm import joinedload
from extensions import db

def register_crud_routes(blueprint, model, schema, url_prefix="", search_fields=None, multipart=False, csv_fields=None, eager_load=None):
    """
    Automatically generates and registers CRUD routes for a given model.

    :param blueprint: The Flask-Smorest Blueprint to register the routes on.
    :param model: The SQLAlchemy model class.
    :param schema: The Marshmallow schema for validation and serialization.
    :param url_prefix: Optional URL prefix (e.g., '/parties').
    :param search_fields: A list of string fields to perform the 'q' search on.
    :param multipart: If True, enables support for file uploads (multipart/form-data).
    :param csv_fields: Optional list of fields to export in the CSV (defaults to all schema fields).
    :param eager_load: A list of relationships to eager load (e.g., ["supplier"]) to optimize queries.
    """

    # Determine the location for incoming data
    # 'form' handles text fields of a multipart request
    # 'json' handles a standard application/json request
    location = "form" if multipart else "json"

    def save_files(data):
        """Saves uploaded files and updates the data dictionary with the filenames."""
        if not multipart:
            return data

        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        # request.files contains the uploaded files
        for key, file_storage in request.files.items():
            if file_storage and file_storage.filename:
                filename = secure_filename(file_storage.filename)
                # Ensure the upload folder exists
                os.makedirs(upload_folder, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_folder, filename)
                file_storage.save(file_path)

                # Update the data with the filename to be saved in the DB
                data[key] = filename
        return data

    def apply_filters_to_query(query):
        """Applies search, date, and sorting filters to the query."""

        # Eager Loading (Optimized Joins)
        if eager_load:
            for relation in eager_load:
                query = query.options(joinedload(getattr(model, relation)))

        # Handle generic search filter 'q'
        q = request.args.get('q')
        if q and search_fields:
            filters = []
            for field in search_fields:
                # Support for searching on related fields (e.g., "supplier.name")
                if '.' in field:
                    rel_name, rel_field = field.split('.', 1)
                    if hasattr(model, rel_name):
                        rel_attr = getattr(model, rel_name)
                        rel_model = rel_attr.property.mapper.class_
                        if hasattr(rel_model, rel_field):
                            # For OR filters, it's safer to use an explicit join
                            query = query.join(getattr(model, rel_name), isouter=True)
                            filters.append(getattr(rel_model, rel_field).ilike(f"%{q}%"))
                elif hasattr(model, field):
                    # Use ilike for case-insensitive search
                    filters.append(getattr(model, field).ilike(f"%{q}%"))

            if filters:
                query = query.filter(or_(*filters))

        # Date filter (created_at)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        if hasattr(model, 'created_at'):
            if date_from:
                query = query.filter(model.created_at >= date_from)
            if date_to:
                query = query.filter(func.date(model.created_at) <= date_to)

        # Sorting
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')

        if sort_by and hasattr(model, sort_by):
            sort_col = getattr(model, sort_by)
            if sort_order == 'desc':
                query = query.order_by(sort_col.desc())
            else:
                query = query.order_by(sort_col.asc())

        return query

    # Routes for the Collection (List and Create)
    @blueprint.route(url_prefix + "/")
    class CollectionResource(MethodView):
        @jwt_required()
        @blueprint.response(200, schema(many=True))
        def get(self):
            """List all items."""
            query = apply_filters_to_query(model.query)

            # Pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            headers = {
                'X-Total-Count': str(pagination.total),
                'X-Pages': str(pagination.pages),
                'X-Current-Page': str(pagination.page),
                'X-Per-Page': str(pagination.per_page)
            }

            return pagination.items, 200, headers

        @jwt_required()
        @blueprint.arguments(schema, location=location)
        @blueprint.response(201, schema)
        def post(self, item_data):
            """Create a new item."""
            item_data = save_files(item_data)
            item = model(**item_data)
            db.session.add(item)
            db.session.commit()
            return item

    # Route for CSV Export
    @blueprint.route(url_prefix + "/export")
    class ExportResource(MethodView):
        @jwt_required()
        @blueprint.response(200, schema={"type": "string"}, content_type="text/csv")
        def get(self):
            """Export filtered data to CSV."""
            # Apply the same filters as the list, but without pagination
            query = apply_filters_to_query(model.query)
            items = query.all()

            # Generate CSV in memory
            string_io = io.StringIO()
            csv_writer = csv.writer(string_io)

            schema_instance = schema()

            # Determine which fields to export:
            # 1. From 'fields' query param (e.g., ?fields=name,email)
            # 2. From the route configuration (csv_fields)
            # 3. Default: all schema fields
            req_fields = request.args.get('fields')
            export_fields = req_fields.split(',') if req_fields else (csv_fields or list(schema_instance.fields.keys()))

            csv_writer.writerow(export_fields)

            for item in items:
                data = schema_instance.dump(item)
                csv_writer.writerow([data.get(f, '') for f in export_fields])

            csv_content = string_io.getvalue()
            headers = {
                "Content-Disposition": "attachment; filename=export.csv"
            }
            return csv_content, 200, headers

    # Routes for a Single Item (Detail, Update, Delete)
    @blueprint.route(url_prefix + "/<int:item_id>")
    class ItemResource(MethodView):
        @jwt_required()
        @blueprint.response(200, schema)
        def get(self, item_id):
            """Retrieve a specific item."""
            return model.query.get_or_404(item_id)

        @jwt_required()
        @blueprint.arguments(schema, location=location)
        @blueprint.response(200, schema)
        def put(self, item_data, item_id):
            """Update an existing item."""
            item = model.query.get_or_404(item_id)

            item_data = save_files(item_data)

            for key, value in item_data.items():
                setattr(item, key, value)
            db.session.commit()
            return item

        @jwt_required()
        @blueprint.response(204)
        def delete(self, item_id):
            """Delete an item."""
            item = model.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()