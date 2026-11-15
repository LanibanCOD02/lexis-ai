"""Add CaseCitation

Revision ID: 5106702923eb
Revises: 6f93f74ec2e5
Create Date: 2026-08-11 22:23:49.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5106702923eb'
down_revision: Union[str, Sequence[str], None] = '6f93f74ec2e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('case_citations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('source_case_id', sa.UUID(), nullable=False),
    sa.Column('target_case_id', sa.UUID(), nullable=True),
    sa.Column('target_case_title', sa.String(length=500), nullable=True),
    sa.Column('source_chunk_id', sa.UUID(), nullable=False),
    sa.Column('citation_text', sa.Text(), nullable=False),
    sa.Column('page_number', sa.Integer(), nullable=True),
    sa.Column('relationship_type', sa.String(length=50), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['source_case_id'], ['cases.id'], ),
    sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
    sa.ForeignKeyConstraint(['target_case_id'], ['cases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_citations_source_case_id'), 'case_citations', ['source_case_id'], unique=False)
    op.create_index(op.f('ix_case_citations_source_chunk_id'), 'case_citations', ['source_chunk_id'], unique=False)
    op.create_index(op.f('ix_case_citations_target_case_id'), 'case_citations', ['target_case_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_case_citations_target_case_id'), table_name='case_citations')
    op.drop_index(op.f('ix_case_citations_source_chunk_id'), table_name='case_citations')
    op.drop_index(op.f('ix_case_citations_source_case_id'), table_name='case_citations')
    op.drop_table('case_citations')
