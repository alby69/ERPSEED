"""Add archetypal tables: Soggetto, Ruolo, Indirizzo, Contatto

Revision ID: f1_add_archetypal_tables
Revises: d8583977de68
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1_add_archetypal_tables'
down_revision = '001_add_tenant_support'
branch_labels = None
depends_on = None


def upgrade():
    # ===== SOGGETTI =====
    op.create_table(
        'soggetti',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('codice', sa.String(length=50), nullable=True),
        sa.Column('tipo_soggetto', sa.String(length=20), nullable=True),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('cognome', sa.String(length=100), nullable=True),
        sa.Column('ragione_sociale', sa.String(length=200), nullable=True),
        sa.Column('partita_iva', sa.String(length=50), nullable=True),
        sa.Column('codice_fiscale', sa.String(length=50), nullable=True),
        sa.Column('email_principale', sa.String(length=120), nullable=True),
        sa.Column('telefono_principale', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('stato', sa.String(length=20), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codice')
    )
    op.create_index('ix_soggetti_codice', 'soggetti', ['codice'])
    op.create_index('ix_soggetti_partita_iva', 'soggetti', ['partita_iva'])
    op.create_index('ix_soggetti_tenant_codice', 'soggetti', ['tenant_id', 'codice'])
    
    # ===== RUOLI =====
    op.create_table(
        'ruoli',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('codice', sa.String(length=30), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('richiede_credito', sa.Boolean(), nullable=True),
        sa.Column('richiede_contratto', sa.Boolean(), nullable=True),
        sa.Column('soggetto_a_fatturazione', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'codice', name='uq_ruolo_tenant_codice')
    )
    op.create_index('ix_ruoli_tenant_id', 'ruoli', ['tenant_id'])
    
    # ===== SOGGETTI_RUOLI (N:N) =====
    op.create_table(
        'soggetti_ruoli',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('soggetto_id', sa.Integer(), nullable=False),
        sa.Column('ruolo_id', sa.Integer(), nullable=False),
        sa.Column('data_inizio', sa.Date(), nullable=True),
        sa.Column('data_fine', sa.Date(), nullable=True),
        sa.Column('stato', sa.String(length=20), nullable=True),
        sa.Column('parametri', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['soggetto_id'], ['soggetti.id']),
        sa.ForeignKeyConstraint(['ruolo_id'], ['ruoli.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('soggetto_id', 'ruolo_id', name='uq_soggetto_ruolo')
    )
    
    # ===== INDIRIZZI =====
    op.create_table(
        'indirizzi',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('denominazione', sa.String(length=200), nullable=True),
        sa.Column('numero_civico', sa.String(length=20), nullable=True),
        sa.Column('CAP', sa.String(length=10), nullable=True),
        sa.Column('città', sa.String(length=100), nullable=False),
        sa.Column('provincia', sa.String(length=50), nullable=True),
        sa.Column('regione', sa.String(length=50), nullable=True),
        sa.Column('nazione', sa.String(length=2), nullable=True),
        sa.Column('latitudine', sa.Float(), nullable=True),
        sa.Column('longitudine', sa.Float(), nullable=True),
        sa.Column('indirizzo_completo', sa.String(length=500), nullable=True),
        sa.Column('tipo', sa.String(length=30), nullable=True),
        sa.Column('geocoded', sa.Boolean(), nullable=True),
        sa.Column('geocoding_data', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_indirizzi_tenant_id', 'indirizzi', ['tenant_id'])
    
    # ===== SOGGETTI_INDIRIZZI (N:N) =====
    op.create_table(
        'soggetti_indirizzi',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('soggetto_id', sa.Integer(), nullable=False),
        sa.Column('indirizzo_id', sa.Integer(), nullable=False),
        sa.Column('tipo_riferimento', sa.String(length=30), nullable=True),
        sa.Column('is_preferred', sa.Boolean(), nullable=True),
        sa.Column('data_inizio', sa.Date(), nullable=True),
        sa.Column('data_fine', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['soggetto_id'], ['soggetti.id']),
        sa.ForeignKeyConstraint(['indirizzo_id'], ['indirizzi.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ===== CONTATTI =====
    op.create_table(
        'contatti',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('canale', sa.String(length=30), nullable=False),
        sa.Column('valore', sa.String(length=255), nullable=False),
        sa.Column('tipo_utilizzo', sa.String(length=30), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('verifica_data', sa.DateTime(), nullable=True),
        sa.Column('is_preferred', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contatti_tenant_id', 'contatti', ['tenant_id'])
    
    # ===== SOGGETTI_CONTATTI (N:N) =====
    op.create_table(
        'soggetti_contatti',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('soggetto_id', sa.Integer(), nullable=False),
        sa.Column('contatto_id', sa.Integer(), nullable=False),
        sa.Column('tipo_riferimento', sa.String(length=30), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['soggetto_id'], ['soggetti.id']),
        sa.ForeignKeyConstraint(['contatto_id'], ['contatti.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('soggetti_contatti')
    op.drop_table('contatti')
    op.drop_table('soggetti_indirizzi')
    op.drop_table('indirizzi')
    op.drop_table('soggetti_ruoli')
    op.drop_table('ruoli')
    op.drop_table('soggetti')
