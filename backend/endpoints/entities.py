from flask import Blueprint, request, jsonify
from flask.views import MethodView
from backend.application.entities import (
    SoggettoCommandHandler, SoggettoQueryHandler,
    RuoloCommandHandler, RuoloQueryHandler,
    SoggettoRuoloCommandHandler,
    IndirizzoCommandHandler, IndirizzoQueryHandler,
    ContattoCommandHandler, ContattoQueryHandler,
    CreateSoggettoCommand, UpdateSoggettoCommand, DeleteSoggettoCommand,
    CreateRuoloCommand, UpdateRuoloCommand, DeleteRuoloCommand,
    AssegnaRuoloCommand, RevocaRuoloCommand,
    IndirizzoData, ContattoData, RuoloAssegnatoData,
)

entities_bp = Blueprint('entities', __name__, url_prefix='/api/entities')


def _get_tenant_id():
    from flask_jwt_extended import get_jwt
    try:
        claims = get_jwt()
        return claims.get('tenant_id', 1)
    except Exception:
        from backend.core.services.tenant_context import TenantContext
        tenant = TenantContext.get_tenant()
        return tenant.id if tenant else 1


def _soggetto_to_dict(soggetto):
    if not soggetto:
        return None
    return {
        'id': soggetto.id,
        'codice': soggetto.codice,
        'tipo_soggetto': soggetto.tipo_soggetto,
        'nome': soggetto.nome,
        'cognome': soggetto.cognome,
        'ragione_sociale': soggetto.ragione_sociale,
        'denominazione': soggetto.denominazione,
        'partita_iva': soggetto.partita_iva,
        'codice_fiscale': soggetto.codice_fiscale,
        'email_principale': soggetto.email_principale,
        'telefono_principale': soggetto.telefono_principale,
        'website': soggetto.website,
        'stato': soggetto.stato,
        'tags': soggetto.tags,
        'ruoli': [
            {
                'ruolo_id': r.ruolo_id,
                'ruolo_codice': r.ruolo_codice,
                'ruolo_nome': r.ruolo_nome,
                'data_inizio': r.data_inizio.isoformat() if r.data_inizio else None,
                'data_fine': r.data_fine.isoformat() if r.data_fine else None,
                'stato': r.stato,
            }
            for r in soggetto.ruoli
        ],
        'indirizzi': [
            {
                'indirizzo_id': i.indirizzo_id,
                'indirizzo': {
                    'id': i.indirizzo.id if i.indirizzo else None,
                    'denominazione': i.indirizzo.denominazione if i.indirizzo else None,
                    'città': i.indirizzo.città if i.indirizzo else None,
                    'provincia': i.indirizzo.provincia if i.indirizzo else None,
                    'nazione': i.indirizzo.nazione if i.indirizzo else None,
                },
                'tipo_riferimento': i.tipo_riferimento,
                'is_preferred': i.is_preferred,
            }
            for i in soggetto.indirizzi
        ],
        'contatti': [
            {
                'contatto_id': c.contatto_id,
                'contatto': {
                    'id': c.contatto.id if c.contatto else None,
                    'canale': c.contatto.canale if c.contatto else None,
                    'valore': c.contatto.valore if c.contatto else None,
                },
                'tipo_riferimento': c.tipo_riferimento,
                'is_primary': c.is_primary,
            }
            for c in soggetto.contatti
        ],
        'created_at': soggetto.created_at.isoformat() if soggetto.created_at else None,
        'updated_at': soggetto.updated_at.isoformat() if soggetto.updated_at else None,
    }


def _ruolo_to_dict(ruolo):
    if not ruolo:
        return None
    return {
        'id': ruolo.id,
        'codice': ruolo.codice,
        'nome': ruolo.nome,
        'descrizione': ruolo.descrizione,
        'categoria': ruolo.categoria,
        'richiede_credito': ruolo.richiede_credito,
        'richiede_contratto': ruolo.richiede_contratto,
        'soggetto_a_fatturazione': ruolo.soggetto_a_fatturazione,
        'is_active': ruolo.is_active,
        'created_at': ruolo.created_at.isoformat() if ruolo.created_at else None,
    }


class SoggettoListView(MethodView):
    def get(self):
        tenant_id = _get_tenant_id()
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)

        handler = SoggettoQueryHandler()
        soggetti = handler.handle_get_all(tenant_id, skip, limit)
        return jsonify([_soggetto_to_dict(s) for s in soggetti])

    def post(self):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        ruoli = []
        if 'ruoli' in data:
            for r in data['ruoli']:
                ruoli.append(RuoloAssegnatoData(
                    ruolo_id=r.get('ruolo_id'),
                    ruolo_codice=r.get('ruolo_codice'),
                    data_inizio=r.get('data_inizio'),
                    data_fine=r.get('data_fine'),
                ))

        indirizzi = []
        if 'indirizzi' in data:
            for i in data['indirizzi']:
                indirizzi.append(IndirizzoData(
                    denominazione=i.get('denominazione'),
                    città=i.get('città', ''),
                    provincia=i.get('provincia'),
                    nazione=i.get('nazione', 'IT'),
                ))

        contatti = []
        if 'contatti' in data:
            for c in data['contatti']:
                contatti.append(ContattoData(
                    canale=c.get('canale', ''),
                    valore=c.get('valore', ''),
                ))

        command = CreateSoggettoCommand(
            tenant_id=tenant_id,
            codice=data['codice'],
            nome=data['nome'],
            tipo_soggetto=data.get('tipo_soggetto', 'persona_fisica'),
            cognome=data.get('cognome'),
            ragione_sociale=data.get('ragione_sociale'),
            partita_iva=data.get('partita_iva'),
            codice_fiscale=data.get('codice_fiscale'),
            email_principale=data.get('email_principale'),
            telefono_principale=data.get('telefono_principale'),
            website=data.get('website'),
            stato=data.get('stato', 'attivo'),
            tags=data.get('tags'),
            ruoli=ruoli,
            indirizzi=indirizzi,
            contatti=contatti,
        )

        handler = SoggettoCommandHandler()
        soggetto = handler.handle_create(command)
        return jsonify(_soggetto_to_dict(soggetto)), 201


class SoggettoDetailView(MethodView):
    def get(self, soggetto_id):
        tenant_id = _get_tenant_id()
        handler = SoggettoQueryHandler()
        soggetto = handler.handle_get_by_id(soggetto_id, tenant_id)
        if not soggetto:
            return jsonify({'error': 'Soggetto not found'}), 404
        return jsonify(_soggetto_to_dict(soggetto))

    def put(self, soggetto_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = UpdateSoggettoCommand(
            id=soggetto_id,
            tenant_id=tenant_id,
            codice=data.get('codice'),
            nome=data.get('nome'),
            tipo_soggetto=data.get('tipo_soggetto'),
            cognome=data.get('cognome'),
            ragione_sociale=data.get('ragione_sociale'),
            partita_iva=data.get('partita_iva'),
            codice_fiscale=data.get('codice_fiscale'),
            email_principale=data.get('email_principale'),
            telefono_principale=data.get('telefono_principale'),
            website=data.get('website'),
            stato=data.get('stato'),
            tags=data.get('tags'),
        )

        handler = SoggettoCommandHandler()
        soggetto = handler.handle_update(command)
        return jsonify(_soggetto_to_dict(soggetto))

    def delete(self, soggetto_id):
        tenant_id = _get_tenant_id()
        command = DeleteSoggettoCommand(id=soggetto_id, tenant_id=tenant_id)
        handler = SoggettoCommandHandler()
        handler.handle_delete(command)
        return '', 204


class SoggettoRuoliView(MethodView):
    def post(self, soggetto_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = AssegnaRuoloCommand(
            soggetto_id=soggetto_id,
            ruolo_id=data['ruolo_id'],
            tenant_id=tenant_id,
            data_inizio=data.get('data_inizio'),
            data_fine=data.get('data_fine'),
            stato=data.get('stato', 'attivo'),
            parametri=data.get('parametri'),
        )

        handler = SoggettoRuoloCommandHandler()
        result = handler.handle_assegna(command)
        return jsonify(result), 201

    def delete(self, soggetto_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = RevocaRuoloCommand(
            soggetto_id=soggetto_id,
            ruolo_id=data['ruolo_id'],
            tenant_id=tenant_id,
        )

        handler = SoggettoRuoloCommandHandler()
        handler.handle_revoca(command)
        return '', 204


class RuoloListView(MethodView):
    def get(self):
        tenant_id = _get_tenant_id()
        handler = RuoloQueryHandler()
        ruoli = handler.handle_get_all(tenant_id)
        return jsonify([_ruolo_to_dict(r) for r in ruoli])

    def post(self):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = CreateRuoloCommand(
            tenant_id=tenant_id,
            codice=data['codice'],
            nome=data['nome'],
            descrizione=data.get('descrizione'),
            categoria=data.get('categoria'),
            richiede_credito=data.get('richiede_credito', False),
            richiede_contratto=data.get('richiede_contratto', False),
            soggetto_a_fatturazione=data.get('soggetto_a_fatturazione', False),
        )

        handler = RuoloCommandHandler()
        ruolo = handler.handle_create(command)
        return jsonify(_ruolo_to_dict(ruolo)), 201


class RuoloDetailView(MethodView):
    def get(self, ruolo_id):
        tenant_id = _get_tenant_id()
        handler = RuoloQueryHandler()
        ruolo = handler.handle_get_by_id(ruolo_id, tenant_id)
        if not ruolo:
            return jsonify({'error': 'Ruolo not found'}), 404
        return jsonify(_ruolo_to_dict(ruolo))

    def put(self, ruolo_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        command = UpdateRuoloCommand(
            id=ruolo_id,
            tenant_id=tenant_id,
            codice=data.get('codice'),
            nome=data.get('nome'),
            descrizione=data.get('descrizione'),
            categoria=data.get('categoria'),
            richiede_credito=data.get('richiede_credito'),
            richiede_contratto=data.get('richiede_contratto'),
            soggetto_a_fatturazione=data.get('soggetto_a_fatturazione'),
            is_active=data.get('is_active'),
        )

        handler = RuoloCommandHandler()
        ruolo = handler.handle_update(command)
        return jsonify(_ruolo_to_dict(ruolo))

    def delete(self, ruolo_id):
        tenant_id = _get_tenant_id()
        command = DeleteRuoloCommand(id=ruolo_id, tenant_id=tenant_id)
        handler = RuoloCommandHandler()
        handler.handle_delete(command)
        return '', 204


entities_bp.add_url_rule('/soggetti', view_func=SoggettoListView.as_view('soggetto_list'))
entities_bp.add_url_rule('/soggetti/<int:soggetto_id>', view_func=SoggettoDetailView.as_view('soggetto_detail'))
entities_bp.add_url_rule('/soggetti/<int:soggetto_id>/ruoli', view_func=SoggettoRuoliView.as_view('soggetto_ruoli'))
entities_bp.add_url_rule('/ruoli', view_func=RuoloListView.as_view('ruolo_list'))
entities_bp.add_url_rule('/ruoli/<int:ruolo_id>', view_func=RuoloDetailView.as_view('ruolo_detail'))


def _indirizzo_to_dict(indirizzo):
    if not indirizzo:
        return None
    return {
        'id': indirizzo.id,
        'denominazione': indirizzo.denominazione,
        'numero_civico': indirizzo.numero_civico,
        'CAP': indirizzo.CAP,
        'città': indirizzo.città,
        'provincia': indirizzo.provincia,
        'regione': indirizzo.regione,
        'nazione': indirizzo.nazione,
        'latitudine': indirizzo.latitudine,
        'longitudine': indirizzo.longitudine,
        'tipo': indirizzo.tipo,
        'created_at': indirizzo.created_at.isoformat() if indirizzo.created_at else None,
        'updated_at': indirizzo.updated_at.isoformat() if indirizzo.updated_at else None,
    }


def _contatto_to_dict(contatto):
    if not contatto:
        return None
    return {
        'id': contatto.id,
        'canale': contatto.canale,
        'valore': contatto.valore,
        'tipo_utilizzo': contatto.tipo_utilizzo,
        'is_verified': contatto.is_verified,
        'is_preferred': contatto.is_preferred,
        'created_at': contatto.created_at.isoformat() if contatto.created_at else None,
        'updated_at': contatto.updated_at.isoformat() if contatto.updated_at else None,
    }


class IndirizzoListView(MethodView):
    def get(self):
        tenant_id = _get_tenant_id()
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)

        handler = IndirizzoQueryHandler()
        indirizzi = handler.handle_get_all(tenant_id, skip, limit)
        return jsonify([_indirizzo_to_dict(i) for i in indirizzi])

    def post(self):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        indirizzo_data = IndirizzoData(
            denominazione=data.get('denominazione'),
            numero_civico=data.get('numero_civico'),
            CAP=data.get('CAP'),
            città=data.get('città', ''),
            provincia=data.get('provincia'),
            regione=data.get('regione'),
            nazione=data.get('nazione', 'IT'),
            latitudine=data.get('latitudine'),
            longitudine=data.get('longitudine'),
            tipo=data.get('tipo'),
        )

        handler = IndirizzoCommandHandler()
        indirizzo = handler.handle_create(indirizzo_data, tenant_id)
        return jsonify(_indirizzo_to_dict(indirizzo)), 201


class IndirizzoDetailView(MethodView):
    def get(self, indirizzo_id):
        tenant_id = _get_tenant_id()
        handler = IndirizzoQueryHandler()
        indirizzo = handler.handle_get_by_id(indirizzo_id, tenant_id)
        if not indirizzo:
            return jsonify({'error': 'Indirizzo not found'}), 404
        return jsonify(_indirizzo_to_dict(indirizzo))

    def put(self, indirizzo_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        indirizzo_data = IndirizzoData(
            denominazione=data.get('denominazione'),
            numero_civico=data.get('numero_civico'),
            CAP=data.get('CAP'),
            città=data.get('città', ''),
            provincia=data.get('provincia'),
            regione=data.get('regione'),
            nazione=data.get('nazione', 'IT'),
            latitudine=data.get('latitudine'),
            longitudine=data.get('longitudine'),
            tipo=data.get('tipo'),
        )

        handler = IndirizzoCommandHandler()
        indirizzo = handler.handle_update(indirizzo_id, indirizzo_data, tenant_id)
        return jsonify(_indirizzo_to_dict(indirizzo))

    def delete(self, indirizzo_id):
        tenant_id = _get_tenant_id()
        handler = IndirizzoCommandHandler()
        handler.handle_delete(indirizzo_id, tenant_id)
        return '', 204


class ContattoListView(MethodView):
    def get(self):
        tenant_id = _get_tenant_id()
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)

        handler = ContattoQueryHandler()
        contatti = handler.handle_get_all(tenant_id, skip, limit)
        return jsonify([_contatto_to_dict(c) for c in contatti])

    def post(self):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        contatto_data = ContattoData(
            canale=data.get('canale', ''),
            valore=data.get('valore', ''),
            tipo_utilizzo=data.get('tipo_utilizzo'),
            is_verified=data.get('is_verified', False),
            is_preferred=data.get('is_preferred', False),
        )

        handler = ContattoCommandHandler()
        contatto = handler.handle_create(contatto_data, tenant_id)
        return jsonify(_contatto_to_dict(contatto)), 201


class ContattoDetailView(MethodView):
    def get(self, contatto_id):
        tenant_id = _get_tenant_id()
        handler = ContattoQueryHandler()
        contatto = handler.handle_get_by_id(contatto_id, tenant_id)
        if not contatto:
            return jsonify({'error': 'Contatto not found'}), 404
        return jsonify(_contatto_to_dict(contatto))

    def put(self, contatto_id):
        tenant_id = _get_tenant_id()
        data = request.get_json()

        contatto_data = ContattoData(
            canale=data.get('canale', ''),
            valore=data.get('valore', ''),
            tipo_utilizzo=data.get('tipo_utilizzo'),
            is_verified=data.get('is_verified', False),
            is_preferred=data.get('is_preferred', False),
        )

        handler = ContattoCommandHandler()
        contatto = handler.handle_update(contatto_id, contatto_data, tenant_id)
        return jsonify(_contatto_to_dict(contatto))

    def delete(self, contatto_id):
        tenant_id = _get_tenant_id()
        handler = ContattoCommandHandler()
        handler.handle_delete(contatto_id, tenant_id)
        return '', 204


entities_bp.add_url_rule('/indirizzi', view_func=IndirizzoListView.as_view('indirizzo_list'))
entities_bp.add_url_rule('/indirizzi/<int:indirizzo_id>', view_func=IndirizzoDetailView.as_view('indirizzo_detail'))
entities_bp.add_url_rule('/contatti', view_func=ContattoListView.as_view('contatto_list'))
entities_bp.add_url_rule('/contatti/<int:contatto_id>', view_func=ContattoDetailView.as_view('contatto_detail'))
