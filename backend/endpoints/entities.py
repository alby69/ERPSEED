from flask import Blueprint, request, jsonify
from flask.views import MethodView
from backend.application.entities import (
    SoggettoCommandHandler, SoggettoQueryHandler,
    RuoloCommandHandler, RuoloQueryHandler,
    SoggettoRuoloCommandHandler,
    CreateSoggettoCommand, UpdateSoggettoCommand, DeleteSoggettoCommand,
    CreateRuoloCommand, UpdateRuoloCommand, DeleteRuoloCommand,
    AssegnaRuoloCommand, RevocaRuoloCommand,
    IndirizzoData, ContattoData, RuoloAssegnatoData,
)

entities_bp = Blueprint('entities', __name__, url_prefix='/api/entities')


def _get_tenant_id():
    return request.headers.get('X-Tenant-ID', type=int) or 1


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
