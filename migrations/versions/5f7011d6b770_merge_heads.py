"""merge heads

Revision ID: 5f7011d6b770
Revises: 273d4507ec04, f1_add_archetypal_tables
Create Date: 2026-02-25 07:30:21.835272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f7011d6b770'
down_revision = ('273d4507ec04', 'f1_add_archetypal_tables')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
