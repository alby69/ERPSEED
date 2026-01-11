import os
import csv
import io
from werkzeug.utils import secure_filename
from flask import request, current_app, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, func, inspect
from sqlalchemy.orm import joinedload
from app.extensions import db

def register_crud_routes(blueprint, model, schema, url_prefix="", search_fields=None, multipart=False, csv_fields=None, eager_load=None):
    """
    Genera e registra automaticamente le rotte CRUD per un dato modello.
    
    :param blueprint: Il Blueprint di Flask-Smorest su cui registrare le rotte
    :param model: Il modello SQLAlchemy
    :param schema: Lo schema Marshmallow per validazione e serializzazione
    :param url_prefix: Prefisso URL opzionale (es. '/parties')
    :param search_fields: Lista di campi (stringhe) su cui effettuare la ricerca 'q'
    :param multipart: Se True, abilita il supporto per upload file (multipart/form-data)
    :param csv_fields: Lista opzionale di campi da esportare nel CSV (default: tutti i campi dello schema)
    :param eager_load: Lista di relazioni da caricare (es. ["supplier"]) per ottimizzare le query e includere dati correlati
    """

    # Determina la location per i dati in ingresso
    # 'form' gestisce i campi testuali di una richiesta multipart
    # 'json' gestisce una richiesta application/json standard
    location = "form" if multipart else "json"

    def save_files(data):
        """Salva i file caricati e aggiorna il dizionario dei dati con i nomi dei file."""
        if not multipart:
            return data
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # request.files contiene i file caricati
        for key, file in request.files.items():
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Assicurati che la cartella esista
                os.makedirs(upload_folder, exist_ok=True)
                
                # Salva il file
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Aggiorna i dati con il nome del file da salvare nel DB
                data[key] = filename
        return data

    def apply_filters(query):
        """Applica filtri di ricerca, data e ordinamento alla query."""
        # Gestione filtro di ricerca generico 'q'
        
        # Eager Loading (Join ottimizzate)
        if eager_load:
            for relation in eager_load:
                query = query.options(joinedload(getattr(model, relation)))

        q = request.args.get('q')
        if q and search_fields:
            filters = []
            for field in search_fields:
            # Supporto per ricerca su campi relazionali (es. "supplier.name")
                if '.' in field:
                    rel_name, rel_field = field.split('.')
                    if hasattr(model, rel_name):
                        rel_attr = getattr(model, rel_name)
                        # Ottieni la classe del modello correlato
                        rel_model = rel_attr.property.mapper.class_
                        if hasattr(rel_model, rel_field):
                            # Join implicita se non già fatta (SQLAlchemy è smart, ma joinedload aiuta)
                            # Nota: per il filtro WHERE serve la join esplicita a volte, 
                            # ma se usiamo joinedload sopra, SQLAlchemy gestisce il path.
                            # Per sicurezza sui filtri OR, usiamo has() o join esplicita.
                            # Qui usiamo un approccio semplice: assumiamo che la relazione esista.
                            filters.append(getattr(rel_model, rel_field).ilike(f"%{q}%"))
                elif hasattr(model, field):
                    # Usa ilike per ricerca case-insensitive
                    filters.append(getattr(model, field).ilike(f"%{q}%"))
            if filters:
            # Se ci sono filtri su relazioni, assicuriamoci che la query faccia la join
            # Questo è un approccio semplificato. Per query complesse servirebbe logica più avanzata.
                for field in search_fields:
                    if '.' in field:
                        rel_name = field.split('.')[0]
                        query = query.join(getattr(model, rel_name))
                query = query.filter(or_(*filters))

        # Filtro per data (created_at)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        if hasattr(model, 'created_at'):
            if date_from:
                query = query.filter(model.created_at >= date_from)
            if date_to:
                query = query.filter(func.date(model.created_at) <= date_to)

        # Ordinamento
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')

        if sort_by and hasattr(model, sort_by):
            sort_col = getattr(model, sort_by)
            if sort_order == 'desc':
                query = query.order_by(sort_col.desc())
            else:
                query = query.order_by(sort_col.asc())

        return query

    # Rotte per la Collezione (Lista e Creazione)
    @blueprint.route(url_prefix + "/")
    class CollectionResource(MethodView):
        @jwt_required()
        @blueprint.response(200, schema(many=True))
        def get(self):
            """Lista tutti gli elementi"""
            query = apply_filters(model.query)

            # Paginazione
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
            """Crea un nuovo elemento"""
            item_data = save_files(item_data)
            item = model(**item_data)
            db.session.add(item)
            db.session.commit()
            return item

    # Rotta per Esportazione CSV
    @blueprint.route(url_prefix + "/export")
    class ExportResource(MethodView):
        @jwt_required()
        def get(self):
            """Esporta i dati filtrati in CSV"""
            # Applica gli stessi filtri della lista, ma senza paginazione
            query = apply_filters(model.query)
            items = query.all()
            
            # Genera CSV in memoria
            si = io.StringIO()
            cw = csv.writer(si)
            
            # Intestazioni (dai campi dello schema)
            schema_instance = schema()
            
            # Determina i campi da esportare:
            # 1. Se specificati via query param 'fields' (es. ?fields=name,email)
            # 2. Se specificati nella configurazione della rotta (csv_fields)
            # 3. Default: tutti i campi dello schema
            req_fields = request.args.get('fields')
            export_fields = req_fields.split(',') if req_fields else (csv_fields or list(schema_instance.fields.keys()))
            
            cw.writerow(export_fields)
            
            for item in items:
                data = schema_instance.dump(item)
                cw.writerow([data.get(f, '') for f in export_fields])
                
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            output.headers["Content-type"] = "text/csv"
            return output

    # Rotte per il Singolo Elemento (Dettaglio, Modifica, Cancellazione)
    @blueprint.route(url_prefix + "/<int:item_id>")
    class ItemResource(MethodView):
        @jwt_required()
        @blueprint.response(200, schema)
        def get(self, item_id):
            """Recupera un elemento specifico"""
            return model.query.get_or_404(item_id)

        @jwt_required()
        @blueprint.arguments(schema, location=location)
        @blueprint.response(200, schema)
        def put(self, item_data, item_id):
            """Aggiorna un elemento esistente"""
            item = model.query.get_or_404(item_id)
            
            item_data = save_files(item_data)
            
            for key, value in item_data.items():
                setattr(item, key, value)
            db.session.commit()
            return item

        @jwt_required()
        @blueprint.response(204)
        def delete(self, item_id):
            """Elimina un elemento"""
            item = model.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()