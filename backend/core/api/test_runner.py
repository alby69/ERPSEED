"""
Test Runner API - Endpoints per la gestione dei test
"""
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from backend.extensions import db

from backend.core.models.test_models import TestSuite, TestCase, TestExecution, ModuleStatusHistory
from backend.core.services.test_engine import TestRunner, TestSuiteGenerator, ModuleStatusManager


class TestCaseSchema(Schema):
    id = fields.Int()
    nome = fields.Str()
    descrizione = fields.Str()
    test_type = fields.Str()
    metodo = fields.Str()
    endpoint = fields.Str()
    payload = fields.Dict()
    expected_status = fields.Int()
    expected_fields = fields.List(fields.Str())
    is_active = fields.Bool()
    ordine = fields.Int()


class TestSuiteSchema(Schema):
    id = fields.Int()
    nome = fields.Str()
    descrizione = fields.Str()
    modulo_target = fields.Str()
    test_type = fields.Str()
    stato = fields.Str()
    is_active = fields.Bool()
    ultimo_esito = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    test_cases = fields.List(fields.Nested(TestCaseSchema))


class TestExecutionSchema(Schema):
    id = fields.Int()
    test_suite_id = fields.Int()
    esito = fields.Str()
    totale_test = fields.Int()
    test_passati = fields.Int()
    test_falliti = fields.Int()
    test_errori = fields.Int()
    durata_secondi = fields.Float()
    dettagli = fields.List(fields.Dict())
    errori = fields.List(fields.Dict())
    environment = fields.Str()
    created_at = fields.DateTime()
    percentuale_successo = fields.Float()


class TestSuiteListResponseSchema(Schema):
    test_suites = fields.List(fields.Nested(TestSuiteSchema))
    total = fields.Int()
    pages = fields.Int()
    current_page = fields.Int()

class TestExecutionListResponseSchema(Schema):
    executions = fields.List(fields.Nested(TestExecutionSchema))

class ModuleStatusResponseSchema(Schema):
    modulo = fields.Str()
    stato = fields.Str()
    storico = fields.List(fields.Dict())

class ModuleStatusChangeSchema(Schema):
    modulo_nome = fields.Str(required=True)
    nuovo_stato = fields.Str(required=True)
    motivo = fields.Str()


class GenerateSuiteSchema(Schema):
    modulo_nome = fields.Str(required=True)
    endpoint_base = fields.Str(required=True)
    tipo = fields.Str(load_default='crud')


blp = Blueprint('test_runner', __name__, url_prefix='/api/v1/tests', description='Test Runner')


@blp.route('/suites')
class TestSuiteList(MethodView):
    @jwt_required()
    @blp.response(200, TestSuiteListResponseSchema)
    def get(self):
        """Lista tutte le test suites con paginazione."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        modulo = request.args.get('modulo')
        search = request.args.get('q')

        query = TestSuite.query

        if modulo:
            query = query.filter_by(modulo_target=modulo)
        if search:
            query = query.filter(TestSuite.nome.ilike(f'%{search}%'))

        pagination = query.order_by(TestSuite.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'test_suites': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }

    @jwt_required()
    @blp.arguments(TestSuiteSchema(exclude=("id", "ultimo_esito", "created_at", "updated_at", "test_cases")))
    @blp.response(201, TestSuiteSchema)
    def post(self, data):
        """Crea una nuova test suite."""
        suite = TestSuite(
            nome=data['nome'], # type: ignore
            descrizione=data.get('descrizione', ''), # type: ignore
            modulo_target=data['modulo_target'], # type: ignore
            test_type=data.get('test_type', 'crud'), # type: ignore
            stato='bozza' # type: ignore
        )
        db.session.add(suite)
        db.session.commit()

        return suite


@blp.route('/suites/<int:suite_id>')
class TestSuiteResource(MethodView):
    @jwt_required()
    @blp.response(200, TestSuiteSchema)
    def get(self, suite_id):
        """Dettagli di una test suite."""
        suite = TestSuite.query.get_or_404(suite_id)
        return suite

    @jwt_required()
    @blp.arguments(TestSuiteSchema(partial=True, exclude=("id", "ultimo_esito", "created_at", "updated_at", "test_cases")))
    @blp.response(200, TestSuiteSchema)
    def put(self, data, suite_id):
        """Aggiorna una test suite."""
        suite = TestSuite.query.get_or_404(suite_id)

        for key, value in data.items():
            if hasattr(suite, key):
                setattr(suite, key, value)

        db.session.commit()
        return suite

    @jwt_required()
    @blp.response(204)
    def delete(self, suite_id):
        """Elimina una test suite."""
        try:
            suite = TestSuite.query.get_or_404(suite_id)

            TestCase.query.filter_by(test_suite_id=suite_id).delete()
            TestExecution.query.filter_by(test_suite_id=suite_id).delete()

            db.session.delete(suite)
            db.session.commit()
            return ''
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))


@blp.route('/suites/<int:suite_id>/cases')
class TestCaseList(MethodView):
    @jwt_required()
    @blp.arguments(TestCaseSchema(exclude=("id",)))
    @blp.response(201, TestCaseSchema)
    def post(self, data, suite_id):
        """Aggiunge un test case alla suite."""
        suite = TestSuite.query.get_or_404(suite_id)

        # Gestione payload se inviato come stringa JSON
        payload = data.get('payload', {})
        if isinstance(payload, str) and payload.strip():
            try:
                import json
                payload = json.loads(payload)
            except:
                pass

        case = TestCase(
            test_suite_id=suite.id, # type: ignore
            nome=data['nome'], # type: ignore
            descrizione=data.get('descrizione', ''), # type: ignore
            test_type=data['test_type'], # type: ignore
            metodo=data['metodo'], # type: ignore
            endpoint=data['endpoint'], # type: ignore
            payload=payload, # type: ignore
            expected_status=data.get('expected_status', 200), # type: ignore
            expected_fields=data.get('expected_fields', []), # type: ignore
            ordine=data.get('ordine', 0) # type: ignore
        )
        db.session.add(case)
        db.session.commit()

        return case


@blp.route('/cases/<int:case_id>')
class TestCaseResource(MethodView):
    @jwt_required()
    @blp.response(200, TestCaseSchema)
    def get(self, case_id):
        """Dettagli di un test case."""
        case = TestCase.query.get_or_404(case_id)
        return case

    @jwt_required()
    @blp.arguments(TestCaseSchema(partial=True, exclude=("id",)))
    @blp.response(200, TestCaseSchema)
    def put(self, data, case_id):
        """Aggiorna un test case."""
        case = TestCase.query.get_or_404(case_id)

        for key, value in data.items():
            if hasattr(case, key):
                if key == 'payload' and isinstance(value, str) and value.strip():
                    try:
                        import json
                        value = json.loads(value)
                    except:
                        pass
                setattr(case, key, value)

        db.session.commit()
        return case

    @jwt_required()
    @blp.response(204)
    def delete(self, case_id):
        """Elimina un test case."""
        case = TestCase.query.get_or_404(case_id)
        db.session.delete(case)
        db.session.commit()
        return ''


@blp.route('/suites/<int:suite_id>/run')
class TestSuiteRun(MethodView):
    @jwt_required()
    @blp.response(200, TestExecutionSchema)
    def post(self, suite_id):
        """Esegue una test suite."""
        identity = get_jwt_identity()
        user_id = int(identity)

        suite = TestSuite.query.get_or_404(suite_id)

        from backend.models import User
        user = User.query.get(user_id)
        tenant_id = user.tenant_id if user else None

        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')

        runner = TestRunner(auth_token=auth_token, tenant_id=tenant_id if tenant_id else 0)

        execution = runner.esegui_suite(suite, user_id)

        return execution


@blp.route('/executions')
class TestExecutionList(MethodView):
    @jwt_required()
    @blp.response(200, TestExecutionListResponseSchema)
    def get(self):
        """Lista tutte le esecuzioni test."""
        limit = request.args.get('limit', 50, type=int)
        suite_id = request.args.get('suite_id', type=int)

        query = TestExecution.query.order_by(TestExecution.created_at.desc())

        if suite_id:
            query = query.filter_by(test_suite_id=suite_id)

        executions = query.limit(limit).all()
        return {'executions': executions}


@blp.route('/executions/<int:exec_id>')
class TestExecutionResource(MethodView):
    @jwt_required()
    @blp.response(200, TestExecutionSchema)
    def get(self, exec_id):
        """Dettagli esecuzione test."""
        execution = TestExecution.query.get_or_404(exec_id)
        return execution

    @jwt_required()
    @blp.response(204)
    def delete(self, exec_id):
        """Elimina esecuzione test."""
        import traceback
        try:
            execution = TestExecution.query.get_or_404(exec_id)
            db.session.delete(execution)
            db.session.commit()
            return ''
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            abort(500, message=str(e))


@blp.route('/generate')
class TestSuiteGeneratorEndpoint(MethodView):
    @jwt_required()
    @blp.arguments(GenerateSuiteSchema)
    @blp.response(201, TestSuiteSchema)
    @blp.alt_response(200, schema=TestSuiteSchema)
    def post(self, data):
        """Genera automaticamente una test suite."""

        tipo = data.get('tipo', 'crud')

        if tipo == 'crud':
            suite = TestSuiteGenerator.genera_crud_suite(
                data['modulo_nome'],
                data['endpoint_base']
            )
            if suite is None:
                abort(400, message=f'Endpoint non valido: {data["endpoint_base"]}. Endpoint validi: soggetti, indirizzi, ruoli, contatti')
        elif tipo == 'validation':
            suite = TestSuiteGenerator.genera_validation_suite(
                data['modulo_nome'],
                data['endpoint_base']
            )
        else:
            abort(400, message=f'Tipo test non supportato: {tipo}')

        existing = TestSuite.query.filter_by(nome=suite.nome).first()
        if existing:
            return existing, 200

        db.session.add(suite)
        db.session.commit()

        return suite


@blp.route('/module/status', methods=['POST'])
class ModuleStatusChange(MethodView):
    @jwt_required()
    @blp.arguments(ModuleStatusChangeSchema)
    @blp.response(200, {"type": "object"})
    def post(self, data):
        """Cambia lo stato di un modulo."""
        identity = get_jwt_identity()
        user_id = int(identity)

        success, message = ModuleStatusManager.cambia_stato(
            data['modulo_nome'],
            data['nuovo_stato'],
            user_id,
            data.get('motivo', '')
        )

        if not success:
            abort(400, message=message)

        return {'message': message}


@blp.route('/module/status/<modulo_nome>')
class ModuleStatusGet(MethodView):
    @jwt_required()
    @blp.response(200, ModuleStatusResponseSchema)
    def get(self, modulo_nome):
        """Stato corrente di un modulo."""
        stato = ModuleStatusManager.get_stato_modulo(modulo_nome)

        if stato is None:
            abort(404, message=f'Modulo {modulo_nome} non trovato')

        history = ModuleStatusHistory.query.filter_by(
            modulo_target=modulo_nome
        ).order_by(ModuleStatusHistory.created_at.desc()).limit(10).all()

        return {
            'modulo': modulo_nome,
            'stato': stato,
            'storico': [
                {
                    'stato_precedente': h.stato_precedente,
                    'stato_nuovo': h.stato_nuovo,
                    'motivo': h.motivo,
                    'utente_id': h.utente_id,
                    'data': h.created_at.isoformat()
                }
                for h in history
            ]
        }


@blp.route('/modules/status')
class AllModulesStatus(MethodView):
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self):
        """Stato di tutti i moduli."""
        suites = TestSuite.query.all()

        return {
            'moduli': [
                {
                    'nome': s.modulo_target,
                    'stato': s.stato,
                    'ultimo_test': s.ultima_esecuzione.esito if s.ultima_esecuzione else None,
                    'ultimo_test_data': s.ultima_esecuzione.created_at.isoformat() if s.ultima_esecuzione else None
                }
                for s in suites
            ]
        }
