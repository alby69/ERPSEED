"""
Endpoint per gestione comuni italiani via database.
Supporta sync con ISTAT e aggiunta manuale.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from flask import request, jsonify
from datetime import datetime
import requests
import json
from backend.entities.comune import Comune, Regione, Provincia
from backend.extensions import db

comuni_blp = Blueprint("comuni", __name__, url_prefix="/api/v1", description="Gestione Comuni Italiani")


@comuni_blp.route("/comuni/regioni")
class RegioniAPI(MethodView):
    def get(self):
        """Lista regioni dal database"""
        regioni = Regione.query.order_by(Regione.nome).all()
        return jsonify([r.to_dict() for r in regioni])


@comuni_blp.route("/comuni/province")
class ProvinceAPI(MethodView):
    def get(self):
        """Lista province, filtrate per regione"""
        regione = request.args.get("regione")
        query = Provincia.query
        if regione:
            query = query.filter_by(codice_regione=regione)
        province = query.order_by(Provincia.nome).all()
        return jsonify([p.to_dict() for p in province])


@comuni_blp.route("/comuni")
class ComuniAPI(MethodView):
    def get(self):
        """Lista comuni con filtri, paginazione e ordinamento"""
        provincia = request.args.get("provincia")
        regione = request.args.get("regione")
        q = request.args.get("q", "")
        
        # Paginazione
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        per_page = min(per_page, 200)  # Max 200 per page
        
        # Ordinamento
        sort_by = request.args.get("sort_by", "nome")
        order = request.args.get("order", "asc")
        
        query = Comune.query
        
        if provincia:
            query = query.filter_by(codice_provincia=provincia)
        if regione:
            query = query.filter_by(codice_regione=regione)
        if q:
            query = query.filter(Comune.nome.ilike(f"%{q}%"))
        
        # Ordinamento
        if sort_by == "nome":
            order_col = Comune.nome
        elif sort_by == "codice":
            order_col = Comune.codice_istat
        elif sort_by == "cap":
            order_col = Comune.cap
        else:
            order_col = Comune.nome
            
        if order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        # Esegui paginazione
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "items": [c.to_dict() for c in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        })
    
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Aggiungi comune manualmente"""
        data = request.json
        
        # Validazione
        if not data.get('nome'):
            return jsonify({"error": "Nome richiesto"}), 400
        
        # Verifica duplicato
        existente = Comune.query.filter_by(codice_istat=data.get('codice_istat')).first()
        if existente:
            return jsonify({"error": "Comune già esistente"}), 409
        
        comune = Comune(
            codice_istat=data.get('codice_istat') or f"M{data.get('nome', '')[:3].upper()}{datetime.now().strftime('%H%M%S')}",
            nome=data.get('nome'),
            denominazione=data.get('denominazione'),
            cap=data.get('cap'),
            codice_provincia=data.get('provincia'),
            codice_regione=data.get('regione'),
            latitudine=data.get('latitudine'),
            longitudine=data.get('longitudine'),
            is_manuale=True,
            source='MANUAL'
        )
        
        db.session.add(comune)
        db.session.commit()
        
        return jsonify(comune.to_dict()), 201


@comuni_blp.route("/comuni/<int:comune_id>")
class ComuneAPI(MethodView):
    def get(self, comune_id):
        """Dettaglio comune"""
        comune = Comune.query.get_or_404(comune_id)
        return jsonify(comune.to_dict())
    
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, comune_id):
        """Modifica comune"""
        comune = Comune.query.get_or_404(comune_id)
        data = request.json
        
        for key in ['nome', 'denominazione', 'cap', 'latitudine', 'longitudine']:
            if key in data:
                setattr(comune, key, data[key])
        
        comune.is_manuale = True
        comune.source = 'MANUAL'
        
        db.session.commit()
        return jsonify(comune.to_dict())
    
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, comune_id):
        """Elimina comune (solo se manuale)"""
        comune = Comune.query.get_or_404(comune_id)
        
        if not comune.is_manuale:
            return jsonify({"error": "Non puoi eliminare comuni ISTAT"}), 403
        
        db.session.delete(comune)
        db.session.commit()
        return '', 204


@comuni_blp.route("/comuni/sync")
class SyncComuniAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """
        Sincronizza comuni da file locale (pre-caricato).
        Usa /admin/comuni/sync/upload per caricare nuovi dati.
        """
        # This endpoint now uses pre-loaded data in the container
        # The actual sync is done via the admin upload endpoint
        return jsonify({
            "success": True,
            "message": "Usa l'endpoint /admin/comuni/sync/upload per caricare dati"
        })


@comuni_blp.route("/admin/comuni/sync/upload")
class AdminSyncUploadAPI(MethodView):
    @comuni_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """
        Carica e sincronizza comuni da file.
        Tipi supportati:
        - CSV (formato ISTAT): codice,nome,provincia,regione,CAP
        - JSON: [{codice_prov_istat, codice_comu_istat, lat, lng}]
        - ZIP (GeoNames): file IT.txt con coordinate
        """
        if 'file' not in request.files:
            return jsonify({"error": "Nessun file caricato"}), 400
        
        uploaded_file = request.files['file']
        sync_type = request.form.get('type', 'comuni')
        
        if uploaded_file.filename == '':
            return jsonify({"error": "Nessun file selezionato"}), 400
        
        return jsonify({
            "success": True,
            "message": f"File ricevuto: {uploaded_file.filename}. Funzionalità di sync in sviluppo.",
            "filename": uploaded_file.filename
        })


@comuni_blp.route("/comuni/stats")
class ComuniStatsAPI(MethodView):
    def get(self):
        """Statistiche comuni"""
        total = Comune.query.count()
        manuali = Comune.query.filter_by(is_manuale=True).count()
        istat = Comune.query.filter_by(source='ISTAT').count()
        
        return jsonify({
            "total": total,
            "manuali": manuali,
            "istat": istat,
            "regioni": Regione.query.count(),
            "province": Provincia.query.count()
        })
