"""Add evidence_id to events

Revision ID: 447ec366ea25
Revises: 958647339a67
Create Date: 2026-07-29 11:01:46.444150

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '447ec366ea25'
down_revision = '958647339a67'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        'events',
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                'evidence_id',
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_index(
            'ix_events_evidence_id',
            ['evidence_id'],
            unique=False
        )

        batch_op.create_foreign_key(
            'fk_events_evidence_id',
            'evidence',
            ['evidence_id'],
            ['id']
        )


def downgrade():

    with op.batch_alter_table(
        'events',
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_events_evidence_id',
            type_='foreignkey'
        )

        batch_op.drop_index(
            'ix_events_evidence_id'
        )

        batch_op.drop_column(
            'evidence_id'
        )