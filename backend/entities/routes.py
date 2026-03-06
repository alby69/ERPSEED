from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import fields
from backend.entities import (
    Soggetto,
    SoggettoRuolo,
    Indirizzo,
    SoggettoIndirizzo,
    Contatto,
    SoggettoContatto,
    Ruolo,
)
from backend.entities.schemas import (
    SoggettoSchema,
    SoggettoCreateSchema,
    RuoloSchema,
    IndirizzoSchema,
    ContattoSchema,
)
from backend.extensions import db, ma
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
    def get(self):
        """Lista soggetti con ordinamento, ricerca e paginazione"""
        query = get_tenant_query(Soggetto)

        # Sorting
        sort_by = request.args.get("sort_by", "nome")
        sort_order = request.args.get("sort_order", "asc")
        if hasattr(Soggetto, sort_by):
            col = getattr(Soggetto, sort_by)
            if sort_order == "desc":
                query = query.order_by(col.desc())
            else:
                query = query.order_by(col.asc())

        # Search by field
        search_field = request.args.get("search_field")
        search_value = request.args.get("search_value")
        if search_field and search_value and hasattr(Soggetto, search_field):
            col = getattr(Soggetto, search_field)
            query = query.filter(col.ilike(f"%{search_value}%"))

        # Global search
        q = request.args.get("q")
        if q:
            query = query.filter(
                (Soggetto.nome.ilike(f"%{q}%"))
                | (Soggetto.codice.ilike(f"%{q}%"))
                | (Soggetto.email_principale.ilike(f"%{q}%"))
            )

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        schema = SoggettoSchema(many=True)
        return {
            "items": schema.dump(pagination.items),
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }

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

        soggetto = Soggetto(**data)
        db.session.add(soggetto)
        db.session.flush()  # Per ottenere l'ID

        # Aggiungi ruoli
        for ruolo_data in ruoli_data:
            sr = SoggettoRuolo(
                soggetto_id=soggetto.id, # type: ignore
                ruolo_id=ruolo_data.get("ruolo_id"), # type: ignore
                stato=ruolo_data.get("stato", "attivo"), # type: ignore
                data_inizio=ruolo_data.get("data_inizio"), # type: ignore
            )
            db.session.add(sr)

        # Aggiungi indirizzi
        for ind_data in indirizzi_data:
            # Crea o riutilizza indirizzo
            indirizzo = Indirizzo(
                tenant_id=tenant_id, # type: ignore
                denominazione=ind_data.get("denominazione"), # type: ignore
                numero_civico=ind_data.get("numero_civico"), # type: ignore
                CAP=ind_data.get("CAP"), # type: ignore
                città=ind_data.get("città"), # type: ignore
                provincia=ind_data.get("provincia"), # type: ignore
                nazione=ind_data.get("nazione", "IT"), # type: ignore
                latitudine=ind_data.get("latitudine"), # type: ignore
                longitudine=ind_data.get("longitudine"), # type: ignore
                tipo=ind_data.get("tipo"), # type: ignore
            )
            db.session.add(indirizzo)
            db.session.flush()

            si = SoggettoIndirizzo(
                soggetto_id=soggetto.id, # type: ignore
                indirizzo_id=indirizzo.id, # type: ignore
                tipo_riferimento=ind_data.get("tipo_riferimento"), # type: ignore
                is_preferred=ind_data.get("is_preferred", False), # type: ignore
            )
            db.session.add(si)

        # Aggiungi contatti
        for cont_data in contatti_data:
            contatto = Contatto(
                tenant_id=tenant_id, # type: ignore
                canale=cont_data.get("canale"), # type: ignore
                valore=cont_data.get("valore"), # type: ignore
                tipo_utilizzo=cont_data.get("tipo_utilizzo"), # type: ignore
                is_preferred=cont_data.get("is_preferred", False), # type: ignore
            )
            db.session.add(contatto)
            db.session.flush()

            sc = SoggettoContatto(
                soggetto_id=soggetto.id, # type: ignore
                contatto_id=contatto.id, # type: ignore
                tipo_riferimento=cont_data.get("tipo_riferimento"), # type: ignore
                is_primary=cont_data.get("is_primary", False), # type: ignore
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
            if key not in ["ruoli", "indirizzi", "contatti"] and hasattr(soggetto, key):
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
        return "", 204


# ==================== RUOLO ====================


@ruolo_blp.route("/ruoli")
class RuoloList(MethodView):
    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Lista ruoli con ordinamento, ricerca e paginazione"""
        query = get_tenant_query(Ruolo)

        # Sorting
        sort_by = request.args.get("sort_by", "nome")
        sort_order = request.args.get("sort_order", "asc")
        if hasattr(Ruolo, sort_by):
            col = getattr(Ruolo, sort_by)
            if sort_order == "desc":
                query = query.order_by(col.desc())
            else:
                query = query.order_by(col.asc())

        # Search by field
        search_field = request.args.get("search_field")
        search_value = request.args.get("search_value")
        if search_field and search_value and hasattr(Ruolo, search_field):
            col = getattr(Ruolo, search_field)
            query = query.filter(col.ilike(f"%{search_value}%"))

        # Global search
        q = request.args.get("q")
        if q:
            query = query.filter(
                (Ruolo.nome.ilike(f"%{q}%"))
                | (Ruolo.codice.ilike(f"%{q}%"))
                | (Ruolo.descrizione.ilike(f"%{q}%"))
            )

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize items manually
        schema = RuoloSchema(many=True)
        return {
            "items": schema.dump(pagination.items),
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }

    @ruolo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @ruolo_blp.arguments(RuoloSchema)
    @ruolo_blp.response(201, RuoloSchema)
    def post(self, data):
        """Crea un nuovo ruolo"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")

        data["tenant_id"] = tenant_id
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
        return "", 204


# ==================== INDIRIZZO ====================


@indirizzo_blp.route("/indirizzi")
class IndirizzoList(MethodView):
    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Lista indirizzi con ordinamento, ricerca e paginazione"""
        query = get_tenant_query(Indirizzo)

        # Sorting
        sort_by = request.args.get("sort_by", "città")
        sort_order = request.args.get("sort_order", "asc")
        if hasattr(Indirizzo, sort_by):
            col = getattr(Indirizzo, sort_by)
            if sort_order == "desc":
                query = query.order_by(col.desc())
            else:
                query = query.order_by(col.asc())

        # Search by field
        search_field = request.args.get("search_field")
        search_value = request.args.get("search_value")
        if search_field and search_value and hasattr(Indirizzo, search_field):
            col = getattr(Indirizzo, search_field)
            query = query.filter(col.ilike(f"%{search_value}%"))

        # Global search
        q = request.args.get("q")
        if q:
            query = query.filter(
                (Indirizzo.città.ilike(f"%{q}%"))
                | (Indirizzo.denominazione.ilike(f"%{q}%"))
                | (Indirizzo.provincia.ilike(f"%{q}%"))
            )

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        schema = IndirizzoSchema(many=True)
        return {
            "items": schema.dump(pagination.items),
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        schema = IndirizzoSchema(many=True)
        return {
            "items": schema.dump(pagination.items),
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }

    @indirizzo_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @indirizzo_blp.arguments(IndirizzoSchema)
    @indirizzo_blp.response(201, IndirizzoSchema)
    def post(self, data):
        """Crea un nuovo indirizzo"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")

        data["tenant_id"] = tenant_id
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
        return "", 204


# ==================== CONTATTO ====================


@contatto_blp.route("/contatti")
class ContattoList(MethodView):
    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Lista contatti con ordinamento, ricerca e paginazione"""
        query = get_tenant_query(Contatto)

        # Sorting
        sort_by = request.args.get("sort_by", "valore")
        sort_order = request.args.get("sort_order", "asc")
        if hasattr(Contatto, sort_by):
            col = getattr(Contatto, sort_by)
            if sort_order == "desc":
                query = query.order_by(col.desc())
            else:
                query = query.order_by(col.asc())

        # Search by field
        search_field = request.args.get("search_field")
        search_value = request.args.get("search_value")
        if search_field and search_value and hasattr(Contatto, search_field):
            col = getattr(Contatto, search_field)
            query = query.filter(col.ilike(f"%{search_value}%"))

        # Global search
        q = request.args.get("q")
        if q:
            query = query.filter(
                (Contatto.valore.ilike(f"%{q}%"))
                | (Contatto.canale.ilike(f"%{q}%"))
            )

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        schema = ContattoSchema(many=True)
        return {
            "items": schema.dump(pagination.items),
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }

    @contatto_blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @contatto_blp.arguments(ContattoSchema)
    @contatto_blp.response(201, ContattoSchema)
    def post(self, data):
        """Crea un nuovo contatto"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")

        data["tenant_id"] = tenant_id
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
        return "", 204
