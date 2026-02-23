from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.entities import Soggetto, SoggettoRuolo, Indirizzo, SoggettoIndirizzo, Contatto, SoggettoContatto, Ruolo
from backend.entities.schemas import (
    SoggettoSchema, SoggettoCreateSchema,
    RuoloSchema,
    IndirizzoSchema,
    ContattoSchema
)
from backend.extensions import db
from backend.core.services.tenant_context import TenantContext


soggetto_blp = Blueprint("soggetti", __name__, description="Operazioni su Soggetti")
ruolo_blp = Blueprint("ruoli", __name__, description="Operazioni su Ruoli")
indirizzo_blp = Blueprint("indirizzi", __name__, description="Operazioni su Indirizzi")
contatto_blp = Blueprint("contatti", __name__, description="Operazioni su Contatti")


def get_tenant_query(model):
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)


# ==================== SOGGETTO ====================

@soggetto_blp.route("/soggetti")
class SoggettoList(MethodView):
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @soggetto_blp.response(200, SoggettoSchema(many=True))
    def get(self):
        """Lista soggetti"""
        query = get_tenant_query(Soggetto)
        return query.all()
    
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @soggetto_blp.arguments(SoggettoCreateSchema)
    @soggetto_blp.response(201, SoggettoSchema)
    def post(self, data):
        """Crea un nuovo soggetto"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        # Estrai ruoli, indirizzi, contatti dalla richiesta
        ruoli_data = data.pop('ruoli', [])
        indirizzi_data = data.pop('indirizzi', [])
        contatti_data = data.pop('contatti', [])
        
        data['tenant_id'] = tenant_id
        
        # Genera codice automatico se non fornito
        if not data.get('codice'):
            last = Soggetto.query.filter_by(tenant_id=tenant_id).order_by(Soggetto.id.desc()).first()
            next_num = (last.id + 1) if last else 1
            data['codice'] = f"SOG{next_num:05d}"
        
        soggetto = Soggetto(**data)
        db.session.add(soggetto)
        db.session.flush()  # Per ottenere l'ID
        
        # Aggiungi ruoli
        for ruolo_data in ruoli_data:
            sr = SoggettoRuolo(
                soggetto_id=soggetto.id,
                ruolo_id=ruolo_data.get('ruolo_id'),
                stato=ruolo_data.get('stato', 'attivo'),
                data_inizio=ruolo_data.get('data_inizio')
            )
            db.session.add(sr)
        
        # Aggiungi indirizzi
        for ind_data in indirizzi_data:
            # Crea o riutilizza indirizzo
            indirizzo = Indirizzo(
                tenant_id=tenant_id,
                denominazione=ind_data.get('denominazione'),
                numero_civico=ind_data.get('numero_civico'),
                CAP=ind_data.get('CAP'),
                città=ind_data.get('città'),
                provincia=ind_data.get('provincia'),
                nazione=ind_data.get('nazione', 'IT'),
                latitudine=ind_data.get('latitudine'),
                longitudine=ind_data.get('longitudine'),
                tipo=ind_data.get('tipo')
            )
            db.session.add(indirizzo)
            db.session.flush()
            
            si = SoggettoIndirizzo(
                soggetto_id=soggetto.id,
                indirizzo_id=indirizzo.id,
                tipo_riferimento=ind_data.get('tipo_riferimento'),
                is_preferred=ind_data.get('is_preferred', False)
            )
            db.session.add(si)
        
        # Aggiungi contatti
        for cont_data in contatti_data:
            contatto = Contatto(
                tenant_id=tenant_id,
                canale=cont_data.get('canale'),
                valore=cont_data.get('valore'),
                tipo_utilizzo=cont_data.get('tipo_utilizzo'),
                is_preferred=cont_data.get('is_preferred', False)
            )
            db.session.add(contatto)
            db.session.flush()
            
            sc = SoggettoContatto(
                soggetto_id=soggetto.id,
                contatto_id=contatto.id,
                tipo_riferimento=cont_data.get('tipo_riferimento'),
                is_primary=cont_data.get('is_primary', False)
            )
            db.session.add(sc)
        
        db.session.commit()
        return soggetto


@soggetto_blp.route("/soggetti/<int:soggetto_id>")
class SoggettoResource(MethodView):
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @soggetto_blp.response(200, SoggettoSchema)
    def get(self, soggetto_id):
        """Dettaglio soggetto"""
        soggetto = get_tenant_query(Soggetto).filter_by(id=soggetto_id).first()
        if not soggetto:
            abort(404, message="Soggetto not found")
        return soggetto
    
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @soggetto_blp.arguments(SoggettoCreateSchema)
    @soggetto_blp.response(200, SoggettoSchema)
    def put(self, data, soggetto_id):
        """Aggiorna soggetto"""
        soggetto = get_tenant_query(Soggetto).filter_by(id=soggetto_id).first()
        if not soggetto:
            abort(404, message="Soggetto not found")
        
        for key, value in data.items():
            if key not in ['ruoli', 'indirizzi', 'contatti'] and hasattr(soggetto, key):
                setattr(soggetto, key, value)
        
        db.session.commit()
        return soggetto
    
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @soggetto_blp.response(204)
    def delete(self, soggetto_id):
        """Elimina soggetto"""
        soggetto = get_tenant_query(Soggetto).filter_by(id=soggetto_id).first()
        if not soggetto:
            abort(404, message="Soggetto not found")
        
        db.session.delete(soggetto)
        db.session.commit()
        return '', 204


# ==================== RUOLO ====================

@ruolo_blp.route("/ruoli")
class RuoloList(MethodView):
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.response(200, RuoloSchema(many=True))
    def get(self):
        """Lista ruoli"""
        return get_tenant_query(Ruolo).all()
    
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.arguments(RuoloSchema)
    @ruolo_blp.response(201, RuoloSchema)
    def post(self, data):
        """Crea un nuovo ruolo"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        data['tenant_id'] = tenant_id
        ruolo = Ruolo(**data)
        
        db.session.add(ruolo)
        db.session.commit()
        return ruolo


@ruolo_blp.route("/ruoli/<int:ruolo_id>")
class RuoloResource(MethodView):
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.response(200, RuoloSchema)
    def get(self, ruolo_id):
        """Dettaglio ruolo"""
        ruolo = get_tenant_query(Ruolo).filter_by(id=ruolo_id).first()
        if not ruolo:
            abort(404, message="Ruolo not found")
        return ruolo
    
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.arguments(RuoloSchema)
    @ruolo_blp.response(200, RuoloSchema)
    def put(self, data, ruolo_id):
        """Aggiorna ruolo"""
        ruolo = get_tenant_query(Ruolo).filter_by(id=ruolo_id).first()
        if not ruolo:
            abort(404, message="Ruolo not found")
        
        for key, value in data.items():
            if hasattr(ruolo, key):
                setattr(ruolo, key, value)
        
        db.session.commit()
        return ruolo
    
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.response(204)
    def delete(self, ruolo_id):
        """Elimina ruolo"""
        ruolo = get_tenant_query(Ruolo).filter_by(id=ruolo_id).first()
        if not ruolo:
            abort(404, message="Ruolo not found")
        
        db.session.delete(ruolo)
        db.session.commit()
        return '', 204


# ==================== INDIRIZZO ====================

@indirizzo_blp.route("/indirizzi")
class IndirizzoList(MethodView):
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.response(200, IndirizzoSchema(many=True))
    def get(self):
        """Lista indirizzi"""
        return get_tenant_query(Indirizzo).all()
    
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.arguments(IndirizzoSchema)
    @indirizzo_blp.response(201, IndirizzoSchema)
    def post(self, data):
        """Crea un nuovo indirizzo"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        data['tenant_id'] = tenant_id
        indirizzo = Indirizzo(**data)
        
        db.session.add(indirizzo)
        db.session.commit()
        return indirizzo


@indirizzo_blp.route("/indirizzi/<int:indirizzo_id>")
class IndirizzoResource(MethodView):
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.response(200, IndirizzoSchema)
    def get(self, indirizzo_id):
        """Dettaglio indirizzo"""
        indirizzo = get_tenant_query(Indirizzo).filter_by(id=indirizzo_id).first()
        if not indirizzo:
            abort(404, message="Indirizzo not found")
        return indirizzo
    
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.arguments(IndirizzoSchema)
    @indirizzo_blp.response(200, IndirizzoSchema)
    def put(self, data, indirizzo_id):
        """Aggiorna indirizzo"""
        indirizzo = get_tenant_query(Indirizzo).filter_by(id=indirizzo_id).first()
        if not indirizzo:
            abort(404, message="Indirizzo not found")
        
        for key, value in data.items():
            if hasattr(indirizzo, key):
                setattr(indirizzo, key, value)
        
        db.session.commit()
        return indirizzo
    
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.response(204)
    def delete(self, indirizzo_id):
        """Elimina indirizzo"""
        indirizzo = get_tenant_query(Indirizzo).filter_by(id=indirizzo_id).first()
        if not indirizzo:
            abort(404, message="Indirizzo not found")
        
        db.session.delete(indirizzo)
        db.session.commit()
        return '', 204


# ==================== CONTATTO ====================

@contatto_blp.route("/contatti")
class ContattoList(MethodView):
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.response(200, ContattoSchema(many=True))
    def get(self):
        """Lista contatti"""
        return get_tenant_query(Contatto).all()
    
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.arguments(ContattoSchema)
    @contatto_blp.response(201, ContattoSchema)
    def post(self, data):
        """Crea un nuovo contatto"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        data['tenant_id'] = tenant_id
        contatto = Contatto(**data)
        
        db.session.add(contatto)
        db.session.commit()
        return contatto


@contatto_blp.route("/contatti/<int:contatto_id>")
class ContattoResource(MethodView):
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.response(200, ContattoSchema)
    def get(self, contatto_id):
        """Dettaglio contatto"""
        contatto = get_tenant_query(Contatto).filter_by(id=contatto_id).first()
        if not contatto:
            abort(404, message="Contatto not found")
        return contatto
    
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.arguments(ContattoSchema)
    @contatto_blp.response(200, ContattoSchema)
    def put(self, data, contatto_id):
        """Aggiorna contatto"""
        contatto = get_tenant_query(Contatto).filter_by(id=contatto_id).first()
        if not contatto:
            abort(404, message="Contatto not found")
        
        for key, value in data.items():
            if hasattr(contatto, key):
                setattr(contatto, key, value)
        
        db.session.commit()
        return contatto
    
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.response(204)
    def delete(self, contatto_id):
        """Elimina contatto"""
        contatto = get_tenant_query(Contatto).filter_by(id=contatto_id).first()
        if not contatto:
            abort(404, message="Contatto not found")
        
        db.session.delete(contatto)
        db.session.commit()
        return '', 204
