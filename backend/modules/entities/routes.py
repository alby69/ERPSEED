from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.modules.entities import (
    Soggetto,
    SoggettoRuolo,
    Indirizzo,
    SoggettoIndirizzo,
    Contatto,
    SoggettoContatto,
    Ruolo,
)
from backend.modules.entities.schemas import (
    SoggettoSchema,
    SoggettoCreateSchema,
    RuoloSchema,
    IndirizzoSchema,
    ContattoSchema,
)
from backend.extensions import db, ma
from backend.core.utils.utils import paginate, apply_filters, apply_sorting
from backend.core.decorators.decorators import tenant_required
from backend.core.services.generic_service import generic_service

soggetto_blp = Blueprint("soggetti", __name__, description="Operazioni su Soggetti")
ruolo_blp = Blueprint("ruoli", __name__, description="Operazioni su Ruoli")
indirizzo_blp = Blueprint("indirizzi", __name__, description="Operazioni su Indirizzi")
contatto_blp = Blueprint("contatti", __name__, description="Operazioni su Contatti")

@soggetto_blp.route("/soggetti")
class SoggettoList(MethodView):
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @soggetto_blp.response(200, SoggettoSchema(many=True))
    def get(self, tenant_id):
        """Lista soggetti con ordinamento, ricerca e paginazione"""
        query = Soggetto.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, Soggetto, ["nome", "codice", "email_principale"])
        query = apply_sorting(query, Soggetto, default_sort_column="nome")
        items, headers = paginate(query)
        return items, 200, headers

    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @soggetto_blp.arguments(SoggettoCreateSchema)
    @soggetto_blp.response(201, SoggettoSchema)
    def post(self, data, tenant_id):
        """Crea un nuovo soggetto"""
        # Estrai ruoli, indirizzi, contatti dalla richiesta
        ruoli_data = data.pop("ruoli", [])
        indirizzi_data = data.pop("indirizzi", [])
        contatti_data = data.pop("contatti", [])
        data["tenant_id"] = tenant_id
        # Genera codice automatico se non fornito
        if not data.get("codice"):
            last = (
                Soggetto.query.filter_by(tenant_id=tenant_id)
                .order_by(Soggetto.id.desc())
                .first()
            )
            next_num = (last.id + 1) if last else 1
            data["codice"] = f"SOG{next_num:05d}"
        soggetto = Soggetto()
        for key, value in data.items():
            setattr(soggetto, key, value)
        db.session.add(soggetto)
        db.session.flush()  # Per ottenere l'ID
        # Aggiungi ruoli
        for ruolo_data in ruoli_data:
            sr = SoggettoRuolo()
            sr.soggetto_id=soggetto.id
            sr.ruolo_id=ruolo_data.get("ruolo_id")
            sr.stato=ruolo_data.get("stato", "attivo")
            sr.data_inizio=ruolo_data.get("data_inizio")
            db.session.add(sr)
        # Aggiungi indirizzi
        for ind_data in indirizzi_data:
            # Crea o riutilizza indirizzo
            indirizzo = Indirizzo()
            indirizzo.tenant_id=tenant_id
            indirizzo.denominazione=ind_data.get("denominazione")
            indirizzo.numero_civico=ind_data.get("numero_civico")
            indirizzo.CAP=ind_data.get("CAP")
            indirizzo.città=ind_data.get("città")
            indirizzo.provincia=ind_data.get("provincia")
            indirizzo.nazione=ind_data.get("nazione", "IT")
            indirizzo.latitudine=ind_data.get("latitudine")
            indirizzo.longitudine=ind_data.get("longitudine")
            indirizzo.tipo=ind_data.get("tipo")
            db.session.add(indirizzo)
            db.session.flush()
            si = SoggettoIndirizzo()
            si.soggetto_id=soggetto.id
            si.indirizzo_id=indirizzo.id
            si.tipo_riferimento=ind_data.get("tipo_riferimento")
            si.is_preferred=ind_data.get("is_preferred", False)
            db.session.add(si)
        # Aggiungi contatti
        for cont_data in contatti_data:
            contatto = Contatto()
            contatto.tenant_id=tenant_id
            contatto.canale=cont_data.get("canale")
            contatto.valore=cont_data.get("valore")
            contatto.tipo_utilizzo=cont_data.get("tipo_utilizzo")
            contatto.is_preferred=cont_data.get("is_preferred", False)
            db.session.add(contatto)
            sc = SoggettoContatto()
            sc.soggetto_id=soggetto.id
            sc.contatto_id=contatto.id
            sc.tipo_riferimento=cont_data.get("tipo_riferimento")
            sc.is_primary=cont_data.get("is_primary", False)
            db.session.add(sc)
        db.session.commit()
        return soggetto

@soggetto_blp.route("/soggetti/<int:soggetto_id>")
class SoggettoResource(MethodView):
    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @soggetto_blp.response(200, SoggettoSchema)
    def get(self, soggetto_id, tenant_id):
        """Dettaglio soggetto"""
        return generic_service.get_tenant_resource(
            Soggetto, soggetto_id, tenant_id, not_found_message="Soggetto not found"
        )

    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @soggetto_blp.arguments(SoggettoSchema)
    @soggetto_blp.response(200, SoggettoSchema)
    def put(self, data, soggetto_id, tenant_id):
        """Aggiorna soggetto"""
        soggetto = Soggetto.query.filter_by(id=soggetto_id, tenant_id=tenant_id).first()
        if not soggetto:
            abort(404, message="Soggetto not found")
        # Estrai e gestisci dati nidificati
        ruoli_data = data.pop("ruoli", None)
        indirizzi_data = data.pop("indirizzi", None)
        contatti_data = data.pop("contatti", None)
        # Aggiorna i campi principali del soggetto
        for key, value in data.items():
            if hasattr(soggetto, key):
                setattr(soggetto, key, value)
        # Gestisci aggiornamento ruoli (sostituzione completa)
        if ruoli_data is not None:
            SoggettoRuolo.query.filter_by(soggetto_id=soggetto.id).delete()
            for ruolo_data in ruoli_data:
                ruolo = Ruolo.query.filter_by(id=ruolo_data.get("ruolo_id"), tenant_id=tenant_id).first()
                if ruolo:
                    sr = SoggettoRuolo(soggetto_id=soggetto.id, ruolo_id=ruolo.id)
                    db.session.add(sr)
        # Gestisci aggiornamento indirizzi (sostituzione completa)
        if indirizzi_data is not None:
            # Eliminiamo i vecchi link, ma non gli indirizzi stessi che potrebbero essere condivisi.
            SoggettoIndirizzo.query.filter_by(soggetto_id=soggetto.id).delete()
            for ind_data in indirizzi_data:
                indirizzo = Indirizzo()
                for k, v in ind_data.items():
                    if k not in ['id', 'tipo_riferimento', 'is_preferred']:
                        setattr(indirizzo, k, v)
                indirizzo.tenant_id = tenant_id
                db.session.add(indirizzo)
                db.session.flush()
                si = SoggettoIndirizzo(
                    soggetto_id=soggetto.id,
                    indirizzo_id=indirizzo.id,
                    tipo_riferimento=ind_data.get("tipo_riferimento"),
                    is_preferred=ind_data.get("is_preferred", False),
                )
                db.session.add(si)
        # Gestisci aggiornamento contatti (sostituzione completa)
        if contatti_data is not None:
            SoggettoContatto.query.filter_by(soggetto_id=soggetto.id).delete()
            for cont_data in contatti_data:
                contatto = Contatto()
                for k, v in cont_data.items():
                    if k not in ['id', 'tipo_riferimento', 'is_primary']:
                        setattr(contatto, k, v)
                contatto.tenant_id = tenant_id
                db.session.add(contatto)
                sc = SoggettoContatto(
                    contatto_id=contatto.id,
                    soggetto_id=soggetto.id,
                    tipo_riferimento=cont_data.get("tipo_riferimento"),
                    is_primary=cont_data.get("is_primary", False),
                )
                db.session.add(sc)
        db.session.commit()
        return soggetto

    @soggetto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @soggetto_blp.response(204)
    def delete(self, soggetto_id, tenant_id):
        """Elimina soggetto"""
        def check_dependencies(soggetto):
            from backend.models import SalesOrder, PurchaseOrder
            if SalesOrder.query.filter_by(customer_id=soggetto.id).first() or \
               PurchaseOrder.query.filter_by(supplier_id=soggetto.id).first():
                abort(409, message="Cannot delete subject with existing sales or purchase orders. Consider deactivating it.")

        generic_service.delete_tenant_resource(
            Soggetto, soggetto_id, tenant_id,
            pre_delete_check=check_dependencies,
            not_found_message="Soggetto not found"
        )
        return "", 204

@ruolo_blp.route("/ruoli")
class RuoloList(MethodView):
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @ruolo_blp.response(200, RuoloSchema(many=True))
    def get(self, tenant_id):
        """Lista ruoli con ordinamento, ricerca e paginazione"""
        query = Ruolo.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, Ruolo, ["nome", "codice", "descrizione"])
        query = apply_sorting(query, Ruolo, default_sort_column="nome")
        items, headers = paginate(query)
        return items, 200, headers

    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @ruolo_blp.arguments(RuoloSchema)
    @ruolo_blp.response(201, RuoloSchema)
    def post(self, data, tenant_id):
        """Crea un nuovo ruolo"""
        return generic_service.create_tenant_resource(Ruolo, data, tenant_id, unique_fields=['codice'])

@ruolo_blp.route("/ruoli/<int:ruolo_id>")
class RuoloResource(MethodView):
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @ruolo_blp.response(200, RuoloSchema)
    def get(self, ruolo_id, tenant_id):
        """Dettaglio ruolo"""
        return generic_service.get_tenant_resource(
            Ruolo, ruolo_id, tenant_id, not_found_message="Ruolo not found"
        )

    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @ruolo_blp.arguments(RuoloSchema)
    @ruolo_blp.response(200, RuoloSchema)
    def put(self, data, ruolo_id, tenant_id):
        """Aggiorna ruolo"""
        return generic_service.update_tenant_resource(
            Ruolo, ruolo_id, tenant_id, data, not_found_message="Ruolo not found"
        )

    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @ruolo_blp.response(204)
    def delete(self, ruolo_id, tenant_id):
        """Elimina ruolo"""
        def check_dependencies(ruolo):
            if SoggettoRuolo.query.filter_by(ruolo_id=ruolo.id).first():
                abort(409, message="Cannot delete a role that is currently assigned to subjects.")
        
        generic_service.delete_tenant_resource(
            Ruolo, ruolo_id, tenant_id,
            pre_delete_check=check_dependencies,
            not_found_message="Ruolo not found"
        )
        return "", 204

@indirizzo_blp.route("/indirizzi")
class IndirizzoList(MethodView):
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @indirizzo_blp.response(200, IndirizzoSchema(many=True))
    def get(self, tenant_id):
        """Lista indirizzi con ordinamento, ricerca e paginazione"""
        query = Indirizzo.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, Indirizzo, ["città", "denominazione", "provincia"])
        query = apply_sorting(query, Indirizzo, default_sort_column="città")
        items, headers = paginate(query)
        return items, 200, headers

    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @indirizzo_blp.arguments(IndirizzoSchema)
    @indirizzo_blp.response(201, IndirizzoSchema)
    def post(self, data, tenant_id):
        """Crea un nuovo indirizzo"""
        return generic_service.create_tenant_resource(Indirizzo, data, tenant_id)

@indirizzo_blp.route("/indirizzi/<int:indirizzo_id>")
class IndirizzoResource(MethodView):
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @indirizzo_blp.response(200, IndirizzoSchema)
    def get(self, indirizzo_id, tenant_id):
        """Dettaglio indirizzo"""
        return generic_service.get_tenant_resource(
            Indirizzo, indirizzo_id, tenant_id, not_found_message="Indirizzo not found"
        )

    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @indirizzo_blp.arguments(IndirizzoSchema)
    @indirizzo_blp.response(200, IndirizzoSchema)
    def put(self, data, indirizzo_id, tenant_id):
        """Aggiorna indirizzo"""
        return generic_service.update_tenant_resource(
            Indirizzo, indirizzo_id, tenant_id, data, not_found_message="Indirizzo not found"
        )

    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @indirizzo_blp.response(204)
    def delete(self, indirizzo_id, tenant_id):
        """Elimina indirizzo"""
        def check_dependencies(indirizzo):
            if SoggettoIndirizzo.query.filter_by(indirizzo_id=indirizzo.id).first():
                abort(409, message="Cannot delete an address that is currently assigned to a subject.")

        generic_service.delete_tenant_resource(
            Indirizzo, indirizzo_id, tenant_id,
            pre_delete_check=check_dependencies,
            not_found_message="Indirizzo not found"
        )
        return "", 204

@contatto_blp.route("/contatti")
class ContattoList(MethodView):
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @contatto_blp.response(200, ContattoSchema(many=True))
    def get(self, tenant_id):
        """Lista contatti con ordinamento, ricerca e paginazione"""
        query = Contatto.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, Contatto, ["valore", "canale"])
        query = apply_sorting(query, Contatto, default_sort_column="valore")
        items, headers = paginate(query)
        return items, 200, headers

    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @contatto_blp.arguments(ContattoSchema)
    @contatto_blp.response(201, ContattoSchema)
    def post(self, data, tenant_id):
        """Crea un nuovo contatto"""
        return generic_service.create_tenant_resource(Contatto, data, tenant_id)

@contatto_blp.route("/contatti/<int:contatto_id>")
class ContattoResource(MethodView):
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @contatto_blp.response(200, ContattoSchema)
    def get(self, contatto_id, tenant_id):
        """Dettaglio contatto"""
        return generic_service.get_tenant_resource(
            Contatto, contatto_id, tenant_id, not_found_message="Contatto not found"
        )

    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @contatto_blp.arguments(ContattoSchema)
    @contatto_blp.response(200, ContattoSchema)
    def put(self, data, contatto_id, tenant_id):
        """Aggiorna contatto"""
        return generic_service.update_tenant_resource(
            Contatto, contatto_id, tenant_id, data, not_found_message="Contatto not found"
        )

    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @contatto_blp.response(204)
    def delete(self, contatto_id, tenant_id):
        """Elimina contatto"""
        def check_dependencies(contatto):
            if SoggettoContatto.query.filter_by(contatto_id=contatto.id).first():
                abort(409, message="Cannot delete a contact that is currently assigned to a subject.")

        generic_service.delete_tenant_resource(
            Contatto, contatto_id, tenant_id,
            pre_delete_check=check_dependencies,
            not_found_message="Contatto not found"
        )
        return "", 204
