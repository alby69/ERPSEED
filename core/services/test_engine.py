"""
Test Engine - Core testing logic for ERPSeed modules
"""
import time
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests

from extensions import db
from core.models.test_models import TestSuite, TestCase, TestExecution, ModuleStatusHistory


class TestResult:
    """Risultato di un singolo test."""

    def __init__(self, test_case: TestCase, esito: str, messaggio: str = '', dettagli: dict = None):
        self.test_case = test_case
        self.esito = esito  # successo, fallito, errore
        self.messaggio = messaggio
        self.dettagli = dettagli or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'test_case_id': self.test_case.id,
            'nome': self.test_case.nome,
            'tipo': self.test_case.test_type,
            'esito': self.esito,
            'messaggio': self.messaggio,
            'dettagli': self.dettagli,
            'timestamp': self.timestamp.isoformat()
        }


class TestRunner:
    """
    Motore di test per eseguire test cases sui moduli FlaskERP.
    Supporta test CRUD, validazione e API.
    """

    def __init__(self, base_url: str = None, auth_token: str = None, tenant_id: int = None):
        if base_url is None:
            base_url = os.getenv('BACKEND_URL', 'http://backend:5000')
        self.base_url = base_url
        self.auth_token = auth_token
        self.tenant_id = tenant_id
        self.session = requests.Session()
        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
        if tenant_id:
            self.session.headers.update({'X-Tenant-ID': str(tenant_id)})

    def _add_tenant_to_payload(self, payload: dict) -> dict:
        """Aggiunge tenant_id al payload se non presente."""
        if payload is None:
            payload = {}
        if self.tenant_id and 'tenant_id' not in payload:
            payload['tenant_id'] = self.tenant_id
        return payload

    def esegui_test_case(self, test_case: TestCase) -> TestResult:
        """Esegue un singolo test case."""
        try:
            if test_case.test_type == 'api':
                return self._test_api(test_case)
            elif test_case.test_type in ('create', 'read', 'update', 'delete'):
                return self._test_crud(test_case)
            elif test_case.test_type == 'validation':
                return self._test_validation(test_case)
            elif test_case.test_type == 'ui':
                return self._test_ui(test_case)
            else:
                return TestResult(test_case, 'errore', f'Tipo test sconosciuto: {test_case.test_type}')
        except Exception as e:
            return TestResult(test_case, 'errore', str(e))

    def _test_api(self, test_case: TestCase) -> TestResult:
        """Test API REST."""
        endpoint = test_case.endpoint.strip('/')
        url = f"{self.base_url}/{endpoint}"
        payload = self._add_tenant_to_payload(test_case.payload)

        timeout = int(os.getenv('TEST_HTTP_TIMEOUT', 30))

        try:
            if test_case.metodo == 'GET':
                response = self.session.get(url, params=payload or {}, timeout=timeout)
            elif test_case.metodo == 'POST':
                response = self.session.post(url, json=payload or {}, timeout=timeout)
            elif test_case.metodo == 'PUT':
                response = self.session.put(url, json=payload or {}, timeout=timeout)
            elif test_case.metodo == 'DELETE':
                response = self.session.delete(url, timeout=timeout)
            else:
                return TestResult(test_case, 'errore', f'Metodo non supportato: {test_case.metodo}')

            status_ok = response.status_code == test_case.expected_status

            if status_ok:
                esito = 'successo'
                messaggio = f'API {test_case.metodo} {test_case.endpoint} - Status {response.status_code}'
                dettagli = {'status_code': response.status_code}

                try:
                    data = response.json()
                    dettagli['response'] = data

                    if test_case.expected_fields:
                        missing = [f for f in test_case.expected_fields if f not in data]
                        if missing:
                            esito = 'fallito'
                            messaggio = f'Campi mancanti: {missing}'
                except:
                    pass
            else:
                esito = 'fallito'
                messaggio = f'Expected {test_case.expected_status}, got {response.status_code}'
                dettagli = {
                    'status_code': response.status_code,
                    'response': response.text[:500]
                }

            return TestResult(test_case, esito, messaggio, dettagli)

        except requests.exceptions.RequestException as e:
            return TestResult(test_case, 'errore', f'Request failed: {str(e)}')

    def _test_crud(self, test_case: TestCase) -> TestResult:
        """Test CRUD generico via API."""
        payload = test_case.payload.copy() if test_case.payload else {}

        if test_case.test_type == 'create' and payload:
            unique_suffix = str(uuid.uuid4())[:4]
            if 'codice' in payload:
                payload['codice'] = f"{payload['codice'][:20]}_{unique_suffix}"
            elif 'nome' in payload:
                payload['nome'] = f"{payload['nome']}_{unique_suffix}"

        test_case.payload = payload
        return self._test_api(test_case)

    def _test_validation(self, test_case: TestCase) -> TestResult:
        """Test di validazione."""
        return self._test_api(test_case)

    def _test_ui(self, test_case: TestCase) -> TestResult:
        """Test UI con Playwright."""
        from playwright.sync_api import sync_playwright

        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        endpoint = test_case.endpoint.strip('/')
        url = f"{frontend_url}/{endpoint}"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Crea un contesto con il token JWT nel localStorage se disponibile
                context = browser.new_context()

                page = context.new_page()

                # Inserimento token per bypassare login se possibile
                if self.auth_token:
                    page.goto(frontend_url)
                    page.evaluate(f"localStorage.setItem('access_token', '{self.auth_token}')")

                page.goto(url)

                # Esegue script custom se presente nel payload
                script = test_case.payload.get('script')
                if script:
                    page.evaluate(script)

                # Verifica presenza elementi
                expected_elements = test_case.payload.get('expected_elements', [])
                missing = []
                for selector in expected_elements:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                    except:
                        missing.append(selector)

                if missing:
                    esito = 'fallito'
                    messaggio = f'Elementi non trovati: {missing}'
                else:
                    esito = 'successo'
                    messaggio = 'Test UI completato con successo'

                dettagli = {
                    'url': url,
                    'title': page.title(),
                    'screenshot_path': f"media/test_screenshots/{test_case.id}_{int(time.time())}.png"
                }

                # Salva screenshot
                os.makedirs('media/test_screenshots', exist_ok=True)
                page.screenshot(path=dettagli['screenshot_path'])

                browser.close()
                return TestResult(test_case, esito, messaggio, dettagli)

        except Exception as e:
            return TestResult(test_case, 'errore', f'Playwright error: {str(e)}')

    def esegui_suite(
        self,
        test_suite: TestSuite,
        user_id: int,
        environment: str = 'test'
    ) -> TestExecution:
        """
        Esegue tutti i test cases di una test suite.
        """
        start_time = time.time()

        execution = TestExecution(
            test_suite_id=test_suite.id,
            utente_id=user_id,
            esito='in_corso',
            environment=environment,
            totale_test=len(test_suite.test_cases)
        )
        db.session.add(execution)
        db.session.commit()

        dettagli = []
        errori = []
        test_passati = 0
        test_falliti = 0
        test_errori = 0

        for test_case in test_suite.test_cases:
            if not test_case.is_active:
                continue

            result = self.esegui_test_case(test_case)
            dettagli.append(result.to_dict())

            if result.esito == 'successo':
                test_passati += 1
            elif result.esito == 'fallito':
                test_falliti += 1
                errori.append({
                    'test': test_case.nome,
                    'messaggio': result.messaggio,
                    'dettagli': result.dettagli
                })
            else:
                test_errori += 1
                errori.append({
                    'test': test_case.nome,
                    'tipo': 'errore',
                    'messaggio': result.messaggio
                })

        durata = time.time() - start_time

        if test_errori > 0:
            esito_finale = 'errore'
        elif test_falliti > 0:
            esito_finale = 'fallito'
        else:
            esito_finale = 'successo'

        execution.esito = esito_finale
        execution.test_passati = test_passati
        execution.test_falliti = test_falliti
        execution.test_errori = test_errori
        execution.durata_secondi = round(durata, 2)
        execution.dettagli = dettagli
        execution.errori = errori

        db.session.commit()

        # Audit logging
        try:
            from shared.utils.audit import create_audit_entry as AuditService
            AuditService.log_action(
                user_id=user_id,
                action='test_execution',
                model_name='TestSuite',
                model_id=test_suite.id,
                project_id=test_suite.id, # Assumiamo che test_suite sia collegata al progetto (se presente)
                changes={
                    'esito': esito_finale,
                    'passati': test_passati,
                    'falliti': test_falliti,
                    'errori': test_errori
                }
            )
        except:
            pass

        return execution


class TestSuiteGenerator:
    """
    Generatore automatico di test suites per i moduli.
    """

    ENTITY_PAYLOADS = {
        'soggetti': {'codice': 'DYNTEST', 'nome': 'Test Soggetto'},
        'indirizzi': {'denominazione': 'Test Indirizzo', 'città': 'Roma', 'provincia': 'RM'},
        'ruoli': {'codice': 'DYNTEST_RUOLO', 'nome': 'Test Ruolo'},
        'contatti': {'canale': 'email', 'valore': 'test@example.com'},
    }

    VALID_ENDPOINTS = ['soggetti', 'indirizzi', 'ruoli', 'contatti']

    @staticmethod
    def genera_crud_suite(modulo_nome: str, endpoint_base: str) -> TestSuite:
        """
        Genera una test suite standard per operazioni CRUD.
        """
        endpoint_base = endpoint_base.strip('/').replace('/api/v1/', '/').replace('/api/v1', '')

        if endpoint_base not in TestSuiteGenerator.VALID_ENDPOINTS:
            return None

        base_payload = TestSuiteGenerator.ENTITY_PAYLOADS.get(modulo_nome, {'nome': 'Test Record'})

        suite = TestSuite(
            nome=f'{modulo_nome}_crud',
            descrizione=f'Test CRUD per il modulo {modulo_nome}',
            modulo_target=modulo_nome,
            test_type='crud',
            stato='bozza'
        )

        test_cases = [
            TestCase(
                nome='List records',
                descrizione='Verifica listing records',
                test_type='read',
                metodo='GET',
                endpoint=f'/{endpoint_base}',
                expected_status=200,
                ordine=1
            ),
            TestCase(
                nome='Create record',
                descrizione='Verifica creazione record',
                test_type='create',
                metodo='POST',
                endpoint=f'/{endpoint_base}',
                payload=base_payload.copy(),
                expected_status=201,
                ordine=2
            ),
        ]

        suite.test_cases = test_cases
        return suite

    @staticmethod
    def genera_validation_suite(modulo_nome: str, endpoint_base: str) -> TestSuite:
        """Genera test suite per validazione campi."""
        suite = TestSuite(
            nome=f'{modulo_nome}_validation',
            descrizione=f'Test validazione per il modulo {modulo_nome}',
            modulo_target=modulo_nome,
            test_type='validation',
            stato='bozza'
        )

        test_cases = [
            TestCase(
                nome='Required field validation',
                descrizione='Verifica errore con campo obbligatorio mancante',
                test_type='validation',
                metodo='POST',
                endpoint=f'/api/v1/{endpoint_base}',
                payload={},
                expected_status=400,
                ordine=1
            ),
            TestCase(
                nome='Unique constraint',
                descrizione='Verifica duplicato',
                test_type='validation',
                metodo='POST',
                endpoint=f'/api/v1/{endpoint_base}',
                payload={'nome': 'Existing'},
                expected_status=409,
                ordine=2
            ),
        ]

        suite.test_cases = test_cases
        return suite


class ModuleStatusManager:
    """
    Gestisce il cambio di stato dei moduli.
    """

    STATI_VALIDI = ['bozza', 'in_test', 'testato', 'pubblicato', 'obsoleto']
    TRANSIZIONI = {
        'bozza': ['in_test'],
        'in_test': ['testato', 'bozza'],
        'testato': ['pubblicato'],
        'pubblicato': ['obsoleto'],
        'obsoleto': []
    }

    @staticmethod
    def cambia_stato(
        modulo_nome: str,
        nuovo_stato: str,
        utente_id: int,
        motivo: str = ''
    ) -> tuple[bool, str]:
        """
        Cambia lo stato di un modulo validando la transizione.
        """
        if nuovo_stato not in ModuleStatusManager.STATI_VALIDI:
            return False, f'Stato non valido: {nuovo_stato}'

        suite = TestSuite.query.filter_by(modulo_target=modulo_nome).first()
        if not suite:
            return False, f'TestSuite non trovata per {modulo_nome}'

        stato_attuale = suite.stato

        if nuovo_stato not in ModuleStatusManager.TRANSIZIONI.get(stato_attuale, []):
            return False, f'Transizione non valida: {stato_attuale} -> {nuovo_stato}'

        if nuovo_stato == 'testato':
            ultimo = TestExecution.query.filter_by(
                test_suite_id=suite.id
            ).order_by(TestExecution.created_at.desc()).first()

            if not ultimo or ultimo.esito != 'successo':
                return False, 'Imposta stato a testato solo se tutti i test passano'

        suite.stato = nuovo_stato

        history = ModuleStatusHistory(
            modulo_target=modulo_nome,
            stato_precedente=stato_attuale,
            stato_nuovo=nuovo_stato,
            utente_id=utente_id,
            motivo=motivo
        )
        db.session.add(history)
        db.session.commit()

        return True, f'Modulo {modulo_nome} -> {nuovo_stato}'

    @staticmethod
    def get_stato_modulo(modulo_nome: str) -> Optional[str]:
        """Restituisce lo stato corrente di un modulo."""
        suite = TestSuite.query.filter_by(modulo_target=modulo_nome).first()
        return suite.stato if suite else None
