"""Initial database schema

Revision ID: 0001
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create contacts table
    op.create_table('contacts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('codementor_username', sa.String(length=255), nullable=True),
                    sa.Column('platform_preference', sa.String(length=50), nullable=True),
                    sa.Column('follow_up_frequency', sa.Integer(), nullable=True),
                    sa.Column('last_contact_date', sa.DateTime(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_name'), 'contacts', ['name'], unique=False)
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_codementor_username'), 'contacts', ['codementor_username'], unique=True)

    # Create message_templates table
    op.create_table('message_templates',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('subject', sa.String(length=500), nullable=True),
                    sa.Column('body', sa.Text(), nullable=False),
                    sa.Column('platform', sa.String(length=50), nullable=False),
                    sa.Column('is_default', sa.Boolean(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_message_templates_id'), 'message_templates', ['id'], unique=False)
    op.create_index(op.f('ix_message_templates_name'), 'message_templates', ['name'], unique=False)
    op.create_index(op.f('ix_message_templates_platform'), 'message_templates', ['platform'], unique=False)

    # Create scheduled_followups table
    op.create_table('scheduled_followups',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('contact_id', sa.Integer(), nullable=False),
                    sa.Column('template_id', sa.Integer(), nullable=False),
                    sa.Column('scheduled_date', sa.DateTime(), nullable=False),
                    sa.Column('status', sa.String(length=50), nullable=True),
                    sa.Column('platform', sa.String(length=50), nullable=False),
                    sa.Column('sent_date', sa.DateTime(), nullable=True),
                    sa.Column('error_message', sa.Text(), nullable=True),
                    sa.Column('retry_count', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
                    sa.ForeignKeyConstraint(['template_id'], ['message_templates.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_scheduled_followups_id'), 'scheduled_followups', ['id'], unique=False)
    op.create_index(op.f('ix_scheduled_followups_contact_id'), 'scheduled_followups', ['contact_id'], unique=False)
    op.create_index(op.f('ix_scheduled_followups_template_id'), 'scheduled_followups', ['template_id'], unique=False)
    op.create_index(op.f('ix_scheduled_followups_scheduled_date'), 'scheduled_followups', ['scheduled_date'], unique=False)
    op.create_index(op.f('ix_scheduled_followups_status'), 'scheduled_followups', ['status'], unique=False)
    op.create_index(op.f('ix_scheduled_followups_platform'), 'scheduled_followups', ['platform'], unique=False)

    # Create platform_credentials table
    op.create_table('platform_credentials',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('platform', sa.String(length=50), nullable=False),
                    sa.Column('encrypted_credentials', sa.Text(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('platform')
                    )
    op.create_index(op.f('ix_platform_credentials_id'), 'platform_credentials', ['id'], unique=False)
    op.create_index(op.f('ix_platform_credentials_platform'), 'platform_credentials', ['platform'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_platform_credentials_platform'), table_name='platform_credentials')
    op.drop_index(op.f('ix_platform_credentials_id'), table_name='platform_credentials')
    op.drop_table('platform_credentials')

    op.drop_index(op.f('ix_scheduled_followups_platform'), table_name='scheduled_followups')
    op.drop_index(op.f('ix_scheduled_followups_status'), table_name='scheduled_followups')
    op.drop_index(op.f('ix_scheduled_followups_scheduled_date'), table_name='scheduled_followups')
    op.drop_index(op.f('ix_scheduled_followups_template_id'), table_name='scheduled_followups')
    op.drop_index(op.f('ix_scheduled_followups_contact_id'), table_name='scheduled_followups')
    op.drop_index(op.f('ix_scheduled_followups_id'), table_name='scheduled_followups')
    op.drop_table('scheduled_followups')

    op.drop_index(op.f('ix_message_templates_platform'), table_name='message_templates')
    op.drop_index(op.f('ix_message_templates_name'), table_name='message_templates')
    op.drop_index(op.f('ix_message_templates_id'), table_name='message_templates')
    op.drop_table('message_templates')

    op.drop_index(op.f('ix_contacts_codementor_username'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')
