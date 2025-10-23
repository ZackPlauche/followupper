"""Add follow-up sequence system

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove follow_up_frequency column from contacts
    op.drop_column('contacts', 'follow_up_frequency')

    # Create followup_sequences table
    op.create_table('followup_sequences',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('platform', sa.String(length=50), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_followup_sequences_id'), 'followup_sequences', ['id'], unique=False)
    op.create_index(op.f('ix_followup_sequences_name'), 'followup_sequences', ['name'], unique=False)
    op.create_index(op.f('ix_followup_sequences_platform'), 'followup_sequences', ['platform'], unique=False)

    # Create followup_sequence_steps table
    op.create_table('followup_sequence_steps',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('sequence_id', sa.Integer(), nullable=False),
                    sa.Column('step_number', sa.Integer(), nullable=False),
                    sa.Column('delay_days', sa.Integer(), nullable=False),
                    sa.Column('template_id', sa.Integer(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['sequence_id'], ['followup_sequences.id'], ),
                    sa.ForeignKeyConstraint(['template_id'], ['message_templates.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_followup_sequence_steps_id'), 'followup_sequence_steps', ['id'], unique=False)
    op.create_index(op.f('ix_followup_sequence_steps_sequence_id'), 'followup_sequence_steps', ['sequence_id'], unique=False)
    op.create_index(op.f('ix_followup_sequence_steps_template_id'), 'followup_sequence_steps', ['template_id'], unique=False)

    # Create contact_sequence_assignments table
    op.create_table('contact_sequence_assignments',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=False),
                    sa.Column('sequence_id', sa.Integer(), nullable=False),
                    sa.Column('status', sa.String(length=50), nullable=True),
                    sa.Column('started_at', sa.DateTime(), nullable=True),
                    sa.Column('completed_at', sa.DateTime(), nullable=True),
                    sa.Column('current_step', sa.Integer(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
                    sa.ForeignKeyConstraint(['sequence_id'], ['followup_sequences.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_contact_sequence_assignments_id'), 'contact_sequence_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_contact_sequence_assignments_contact_id'), 'contact_sequence_assignments', ['contact_id'], unique=False)
    op.create_index(op.f('ix_contact_sequence_assignments_sequence_id'), 'contact_sequence_assignments', ['sequence_id'], unique=False)
    op.create_index(op.f('ix_contact_sequence_assignments_status'), 'contact_sequence_assignments', ['status'], unique=False)


def downgrade() -> None:
    # Drop new tables
    op.drop_index(op.f('ix_contact_sequence_assignments_status'), table_name='contact_sequence_assignments')
    op.drop_index(op.f('ix_contact_sequence_assignments_sequence_id'), table_name='contact_sequence_assignments')
    op.drop_index(op.f('ix_contact_sequence_assignments_contact_id'), table_name='contact_sequence_assignments')
    op.drop_index(op.f('ix_contact_sequence_assignments_id'), table_name='contact_sequence_assignments')
    op.drop_table('contact_sequence_assignments')

    op.drop_index(op.f('ix_followup_sequence_steps_template_id'), table_name='followup_sequence_steps')
    op.drop_index(op.f('ix_followup_sequence_steps_sequence_id'), table_name='followup_sequence_steps')
    op.drop_index(op.f('ix_followup_sequence_steps_id'), table_name='followup_sequence_steps')
    op.drop_table('followup_sequence_steps')

    op.drop_index(op.f('ix_followup_sequences_platform'), table_name='followup_sequences')
    op.drop_index(op.f('ix_followup_sequences_name'), table_name='followup_sequences')
    op.drop_index(op.f('ix_followup_sequences_id'), table_name='followup_sequences')
    op.drop_table('followup_sequences')

    # Add back follow_up_frequency column
    op.add_column('contacts', sa.Column('follow_up_frequency', sa.Integer(), nullable=True))
