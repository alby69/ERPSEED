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
    ultimo_esito = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
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
    def get(self):
        """Lista tutte le test suites."""
        suites = TestSuite.query.order_by(TestSuite.created_at.desc()).all()
        return {'test_suites': TestSuiteSchema(many=True).dump(suites)}
    
    @jwt_required()
    def post(self):
        """Crea una nuova test suite."""
        data = request.get_json()
        
        suite = TestSuite(
            nome=data['nome'],
            descrizione=data.get('descrizione', ''),
            modulo_target=data['modulo_target'],
            test_type=data.get('test_type', 'crud'),
            stato='bozza'
        )
        db.session.add(suite)
        db.session.commit()
        
        return TestSuiteSchema().dump(suite), 201


@blp.route('/suites/<int:suite_id>')
class TestSuiteResource(MethodView):
    @jwt_required()
    def get(self, suite_id):
        """Dettagli di una test suite."""
        suite = TestSuite.query.get_or_404(suite_id)
        return TestSuiteSchema().dump(suite)
    
    @jwt_required()
    def put(self, suite_id):
        """Aggiorna una test suite."""
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(suite, key):
                setattr(suite, key, value)
        
        db.session.commit()
        return TestSuiteSchema().dump(suite)
    
    @jwt_required()
    def delete(self, suite_id):
        """Elimina una test suite."""
        try:
            suite = TestSuite.query.get_or_404(suite_id)
            
            TestCase.query.filter_by(test_suite_id=suite_id).delete()
            TestExecution.query.filter_by(test_suite_id=suite_id).delete()
            
            db.session.delete(suite)
            db.session.commit()
            return {'message': 'TestSuite eliminata'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


@blp.route('/suites/<int:suite_id>/cases')
class TestCaseList(MethodView):
    @jwt_required()
    def post(self, suite_id):
        """Aggiunge un test case alla suite."""
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        
        case = TestCase(
            test_suite_id=suite.id,
            nome=data['nome'],
            descrizione=data.get('descrizione', ''),
            test_type=data['test_type'],
            metodo=data['metodo'],
            endpoint=data['endpoint'],
            payload=data.get('payload', {}),
            expected_status=data.get('expected_status', 200),
            expected_fields=data.get('expected_fields', []),
            ordine=data.get('ordine', 0)
        )
        db.session.add(case)
        db.session.commit()
        
        return TestCaseSchema().dump(case), 201


@blp.route('/suites/<int:suite_id>/run')
class TestSuiteRun(MethodView):
    @jwt_required()
    def post(self, suite_id):
        """Esegue una test suite."""
        identity = get_jwt_identity()
        user_id = int(identity)
        
        suite = TestSuite.query.get_or_404(suite_id)
        
        from backend.models import User
        user = User.query.get(user_id)
        tenant_id = user.tenant_id if user else None
        
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        base_url = 'http://backend:5000/api/v1'
        
        runner = TestRunner(base_url=base_url, auth_token=auth_token, tenant_id=tenant_id)
        
        execution = runner.esegui_suite(suite, user_id)
        
        return TestExecutionSchema().dump(execution)


@blp.route('/executions')
class TestExecutionList(MethodView):
    @jwt_required()
    def get(self):
        """Lista tutte le esecuzioni test."""
        limit = request.args.get('limit', 50, type=int)
        suite_id = request.args.get('suite_id', type=int)
        
        query = TestExecution.query.order_by(TestExecution.created_at.desc())
        
        if suite_id:
            query = query.filter_by(test_suite_id=suite_id)
        
        executions = query.limit(limit).all()
        return {'executions': TestExecutionSchema(many=True).dump(executions)}


@blp.route('/executions/<int:exec_id>')
class TestExecutionResource(MethodView):
    @jwt_required()
    def get(self, exec_id):
        """Dettagli esecuzione test."""
        execution = TestExecution.query.get_or_404(exec_id)
        return TestExecutionSchema().dump(execution)
    
    @jwt_required()
    def delete(self, exec_id):
        """Elimina esecuzione test."""
        import traceback
        try:
            execution = TestExecution.query.get_or_404(exec_id)
            db.session.delete(execution)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return {'error': str(e)}, 500


@blp.route('/generate')
class TestSuiteGeneratorEndpoint(MethodView):
    @jwt_required()
    def post(self):
        """Genera automaticamente una test suite."""
        data = request.get_json()
        
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
            return TestSuiteSchema().dump(existing), 200
        
        db.session.add(suite)
        db.session.commit()
        
        return TestSuiteSchema().dump(suite), 201


@blp.route('/module/status', methods=['POST'])
class ModuleStatusChange(MethodView):
    @jwt_required()
    def post(self):
        """Cambia lo stato di un modulo."""
        identity = get_jwt_identity()
        user_id = int(identity)
        
        data = request.get_json()
        
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
