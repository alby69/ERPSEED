"""
Endpoint per gestione comuni italiani via database.
Supporta sync con ISTAT e aggiunta manuale.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from flask import request
from datetime import datetime
from backend.modules.entities.comune import Comune, Regione, Provincia
from backend.extensions import db, ma
from backend.core.schemas.schemas import BaseSchema
from backend.core.services.generic_service import generic_service
from marshmallow import Schema, fields

comuni_blp = Blueprint("comuni", __name__, url_prefix="/comuni", description="Gestione Comuni Italiani")

# Schemas for validation
class ComuneSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Comune
        load_instance = False
        dump_only = ("id",)

class FileUploadSchema(Schema):
    file = fields.Raw(metadata={"type": "file"}, required=True)
    type = fields.Str(load_default='comuni')

@comuni_blp.route("/regioni")
class RegioniAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Lista regioni dal database"""
        regioni = Regione.query.order_by(Regione.nome).all()
        return [r.to_dict() for r in regioni]

@comuni_blp.route("/province")
class ProvinceAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Lista province, filtrate per regione"""
        regione = request.args.get("regione")
        query = Provincia.query
        if regione:
            query = query.filter_by(codice_regione=regione)
        province = query.order_by(Provincia.nome).all()
        return [p.to_dict() for p in province]

@comuni_blp.route("")
class ComuniAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.response(200, ComuneSchema(many=True))
    def get(self):
        """Lista comuni con filtri, paginazione e ordinamento"""
        from backend.core.utils.utils import apply_filters, apply_sorting, paginate
        query = Comune.query
        # Apply standard filters
        query = apply_filters(query, Comune, ['nome', 'codice_istat', 'cap'])
        if request.args.get("provincia"):
            query = query.filter_by(codice_provincia=request.args.get("provincia"))
        if request.args.get("regione"):
            query = query.filter_by(codice_regione=request.args.get("regione"))
        query = apply_sorting(query, Comune)
        # Paginate and return items with headers
        items, headers = paginate(query)
        return items, 200, headers
    
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.arguments(ComuneSchema)
    @comuni_blp.response(201, ComuneSchema)
    def post(self, data):
        """Aggiungi comune manualmente"""
        # Validazione
        if not data.get('nome'):
            abort(400, message="Nome del comune è richiesto.")
        
        # Verifica duplicato
        existente = Comune.query.filter_by(codice_istat=data.get('codice_istat')).first()
        if existente:
            abort(409, message=f"Comune con codice ISTAT {data.get('codice_istat')} già esistente.")
        
        comune = Comune()
        comune.codice_istat = data.get('codice_istat') or f"M{data.get('nome', '')[:3].upper()}{datetime.now().strftime('%H%M%S')}"
        comune.nome = data.get('nome')
        comune.denominazione = data.get('denominazione')
        comune.cap = data.get('cap')
        comune.codice_provincia = data.get('codice_provincia')
        comune.codice_regione = data.get('codice_regione')
        comune.latitudine = data.get('latitudine')
        comune.longitudine = data.get('longitudine')
        comune.is_manuale = True
        comune.source = 'MANUAL'
        db.session.add(comune)
        db.session.commit()
        return comune

@comuni_blp.route("/<int:comune_id>")
class ComuneAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.response(200, ComuneSchema)
    def get(self, comune_id):
        """Dettaglio comune"""
        return generic_service.get_resource(Comune, comune_id)

    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.arguments(ComuneSchema(partial=True))
    @comuni_blp.response(200, ComuneSchema)
    def put(self, data, comune_id):
        """Modifica comune"""
        comune = Comune.query.get_or_404(comune_id)
        for key in ['nome', 'denominazione', 'cap', 'latitudine', 'longitudine']:
            if key in data:
                setattr(comune, key, data[key])
        db.session.commit()
        return comune

    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.response(204)
    def delete(self, comune_id):
        """Elimina comune (solo se manuale)"""
        def check_manual(comune):
            if not comune.is_manuale:
                abort(403, message="Non è possibile eliminare comuni ISTAT.")

        generic_service.delete_resource(
            Comune, comune_id,
            pre_delete_check=check_manual
        )
        return '', 204

@comuni_blp.route("/sync")
class SyncComuniAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """
        Sincronizza comuni da file locale (pre-caricato).
        """
        return {
            "success": True,
            "message": "Usa l'endpoint /admin/comuni/sync/upload per caricare dati"
        }

@comuni_blp.route("/admin/sync/upload")
class AdminSyncUploadAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @comuni_blp.arguments(FileUploadSchema, location="files")
    @comuni_blp.response(200)
    def post(self, files_data):
        """Carica e sincronizza comuni da file."""
        uploaded_file = files_data['file']
        if not uploaded_file or uploaded_file.filename == '':
            abort(400, message="Nessun file selezionato.")
        
        return {
            "message": f"File ricevuto: {uploaded_file.filename}. Funzionalità di sync in sviluppo.",
            "filename": uploaded_file.filename
        }

@comuni_blp.route("/stats")
class ComuniStatsAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Statistiche comuni"""
        total = Comune.query.count()
        manuali = Comune.query.filter_by(is_manuale=True).count()
        istat = Comune.query.filter_by(source='ISTAT').count()
        
        return {
            "total": total,
            "manuali": manuali,
            "istat": istat,
            "regioni": Regione.query.count(),
            "province": Provincia.query.count()
        }
