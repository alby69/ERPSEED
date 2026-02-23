"""
Test Models - TestSuite, TestCase, TestExecution
Sistema di testing per i moduli FlaskERP
"""
from datetime import datetime
from backend.core.models.base import BaseModel
from backend.extensions import db


class TestSuite(BaseModel):
    """
    Raggruppa una serie di test cases per un modulo specifico.
    """
    __tablename__ = 'test_suites'
    
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descrizione = db.Column(db.Text)
    modulo_target = db.Column(db.String(50), nullable=False, index=True)
    
    test_type = db.Column(
        db.String(20),
        default='crud',
        comment="Tipo: crud, validation, api, permission, full"
    )
    
    stato = db.Column(
        db.String(20),
        default='bozza',
        comment="Stato: bozza, in_test, testato, pubblicato, obsoleto"
    )
    
    is_active = db.Column(db.Boolean, default=True)
    
    test_cases = db.relationship(
        'TestCase',
        back_populates='test_suite',
        cascade='all, delete-orphan',
        order_by='TestCase.ordine'
    )
    
    executions = db.relationship(
        'TestExecution',
        back_populates='test_suite',
        cascade='all, delete-orphan',
        order_by='TestExecution.created_at.desc()'
    )
    
    def __repr__(self):
        return f'<TestSuite {self.nome}>'
    
    @property
    def ultimo_esito(self):
        if self.executions:
            return self.executions[0].esito
        return None
    
    @property
    def ultima_esecuzione(self):
        if self.executions:
            return self.executions[0]
        return None


class TestCase(BaseModel):
    """
    Rappresenta un singolo test case all'interno di una test suite.
    """
    __tablename__ = 'test_cases'
    
    test_suite_id = db.Column(
        db.Integer,
        db.ForeignKey('test_suites.id'),
        nullable=False,
        index=True
    )
    
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    
    ordine = db.Column(db.Integer, default=0)
    
    test_type = db.Column(
        db.String(30),
        nullable=False,
        comment="Tipo: create, read, update, delete, validation, api"
    )
    
    metodo = db.Column(
        db.String(50),
        nullable=False,
        comment="HTTP method: GET, POST, PUT, DELETE"
    )
    
    endpoint = db.Column(db.String(200), nullable=False)
    
    payload = db.Column(db.JSON, default=dict)
    
    expected_status = db.Column(db.Integer, default=200)
    
    expected_fields = db.Column(db.JSON, default=list)
    
    validation_rules = db.Column(db.JSON, default=dict)
    
    is_active = db.Column(db.Boolean, default=True)
    
    test_suite = db.relationship('TestSuite', back_populates='test_cases')
    
    def __repr__(self):
        return f'<TestCase {self.nome}>'


class TestExecution(BaseModel):
    """
    Registra l'esecuzione di una test suite.
    """
    __tablename__ = 'test_executions'
    
    test_suite_id = db.Column(
        db.Integer,
        db.ForeignKey('test_suites.id'),
        nullable=False,
        index=True
    )
    
    utente_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    
    esito = db.Column(
        db.String(20),
        default='in_corso',
        comment="Esito: in_corso, successo, fallito, errore"
    )
    
    totale_test = db.Column(db.Integer, default=0)
    test_passati = db.Column(db.Integer, default=0)
    test_falliti = db.Column(db.Integer, default=0)
    test_errori = db.Column(db.Integer, default=0)
    
    durata_secondi = db.Column(db.Float, default=0.0)
    
    dettagli = db.Column(db.JSON, default=list)
    
    errori = db.Column(db.JSON, default=list)
    
    note = db.Column(db.Text)
    
    environment = db.Column(
        db.String(20),
        default='test',
        comment="Environment: test, production"
    )
    
    test_suite = db.relationship('TestSuite', back_populates='executions')
    utente = db.relationship('User')
    
    def __repr__(self):
        return f'<TestExecution {self.id} - {self.esito}>'
    
    @property
    def percentuale_successo(self):
        if self.totale_test == 0:
            return 0
        return round((self.test_passati / self.totale_test) * 100, 1)
    
    @property
    def data_formattata(self):
        return self.created_at.strftime('%d/%m/%Y %H:%M')


class ModuleStatusHistory(BaseModel):
    """
    Storico dei cambi di stato dei moduli.
    """
    __tablename__ = 'module_status_history'
    
    modulo_target = db.Column(db.String(50), nullable=False, index=True)
    
    stato_precedente = db.Column(db.String(20))
    stato_nuovo = db.Column(db.String(20), nullable=False)
    
    utente_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    
    motivo = db.Column(db.Text)
    
    utente = db.relationship('User')
    
    def __repr__(self):
        return f'<ModuleStatusHistory {self.modulo_target}: {self.stato_precedente} -> {self.stato_nuovo}>'
