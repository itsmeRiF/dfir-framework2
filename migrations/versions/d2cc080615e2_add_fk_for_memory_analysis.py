"""Add FK for memory analysis

Revision ID: d2cc080615e2
Revises: d3fb01d96e25
Create Date: 2026-07-27 17:43:20.871988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2cc080615e2'
down_revision = 'd3fb01d96e25'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("memory_analysis", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_memory_analysis_case_id"),
            ["case_id"],
            unique=False
        )

        batch_op.create_foreign_key(
            "fk_memory_analysis_case_id",
            "cases",
            ["case_id"],
            ["id"]
        )


def downgrade():
    with op.batch_alter_table("memory_analysis", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_memory_analysis_case_id",
            type_="foreignkey"
        )

        batch_op.drop_index(
            batch_op.f("ix_memory_analysis_case_id")
        )
