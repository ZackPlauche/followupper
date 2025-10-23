"""Flask API backend for Followupper application."""

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import emoji

from .models.database import engine, Base
from .models.contact import Contact
from .models.message_template import MessageTemplate
from .models.scheduled_followup import ScheduledFollowup
from .models.platform_credentials import PlatformCredentials
from .models.followup_sequence import FollowupSequence
from .models.followup_sequence_step import FollowupSequenceStep
from .models.contact_sequence_assignment import ContactSequenceAssignment

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Nuxt frontend


def get_db():
    """Get database session."""
    return Session(engine)


def run_migrations():
    """Run database migrations."""
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Error running migrations: {e}")
        # Fallback: create tables directly
        Base.metadata.create_all(bind=engine)


# Initialize database
run_migrations()

# API Routes


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts."""
    try:
        db = get_db()
        contacts = db.query(Contact).order_by(Contact.name).all()

        result = []
        for contact in contacts:
            result.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'codementor_username': contact.codementor_username,
                'platform_preference': contact.platform_preference,
                'last_contact_date': contact.last_contact_date.isoformat() if contact.last_contact_date else None,
                'notes': contact.notes,
                'is_active': contact.is_active,
                'created_at': contact.created_at.isoformat() if contact.created_at else None,
                'updated_at': contact.updated_at.isoformat() if contact.updated_at else None
            })

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts', methods=['POST'])
def create_contact():
    """Create a new contact."""
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug log
        db = Session(engine)

        # Convert empty strings to None for unique fields
        email = data.get('email') if data.get('email') else None
        codementor_username = data.get('codementor_username') if data.get('codementor_username') else None

        contact = Contact(
            name=data['name'],
            email=email,
            codementor_username=codementor_username,
            platform_preference=data.get('platform_preference', 'email'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )

        db.add(contact)
        db.commit()

        # Get the ID before closing the session
        contact_id = contact.id

        db.close()

        return jsonify({'id': contact_id, 'message': 'Contact created successfully'}), 201
    except Exception as e:
        print(f"Error creating contact: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact."""
    try:
        data = request.get_json()
        db = Session(engine)

        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            db.close()
            return jsonify({'error': 'Contact not found'}), 404

        # Convert empty strings to None for unique fields
        email = data.get('email') if data.get('email') else None
        codementor_username = data.get('codementor_username') if data.get('codementor_username') else None

        contact.name = data['name']
        contact.email = email
        contact.codementor_username = codementor_username
        contact.platform_preference = data.get('platform_preference', 'email')
        contact.notes = data.get('notes')
        contact.is_active = data.get('is_active', True)
        contact.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.close()

        return jsonify({'message': 'Contact updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact."""
    try:
        db = Session(engine)
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            db.close()
            return jsonify({'error': 'Contact not found'}), 404

        db.delete(contact)
        db.commit()
        db.close()

        return jsonify({'message': 'Contact deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all message templates."""
    try:
        db = Session(engine)
        templates = db.query(MessageTemplate).order_by(MessageTemplate.name).all()

        result = []
        for template in templates:
            result.append({
                'id': template.id,
                'name': template.name,
                'subject': template.subject,
                'body': template.body,
                'is_default': template.is_default,
                'is_active': template.is_active,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None
            })

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new message template."""
    try:
        data = request.get_json()
        print(f"Received template data: {data}")  # Debug log
        db = Session(engine)

        template = MessageTemplate(
            name=data['name'],
            subject=data.get('subject', ''),
            body=data['body'],
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True)
        )

        db.add(template)
        db.commit()
        template_id = template.id
        db.close()

        return jsonify({'id': template_id, 'message': 'Template created successfully'}), 201
    except Exception as e:
        print(f"Error creating template: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update a message template."""
    try:
        data = request.get_json()
        db = Session(engine)

        template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
        if not template:
            db.close()
            return jsonify({'error': 'Template not found'}), 404

        template.name = data['name']
        template.subject = data.get('subject', '')
        template.body = data['body']
        template.is_default = data.get('is_default', False)
        template.is_active = data.get('is_active', True)
        template.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.close()

        return jsonify({'message': 'Template updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a message template."""
    try:
        db = Session(engine)
        template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
        if not template:
            db.close()
            return jsonify({'error': 'Template not found'}), 404

        db.delete(template)
        db.commit()
        db.close()

        return jsonify({'message': 'Template deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates/<int:template_id>/preview', methods=['POST'])
def preview_template(template_id):
    """Preview a template with contact data."""
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')

        db = Session(engine)
        template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
        if not template:
            db.close()
            return jsonify({'error': 'Template not found'}), 404

        if contact_id:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                db.close()
                return jsonify({'error': 'Contact not found'}), 404
        else:
            # Use first contact as default
            contact = db.query(Contact).first()
            if not contact:
                db.close()
                return jsonify({'error': 'No contacts available for preview'}), 400

        # Render template with contact data
        rendered = template.render_template(contact)

        db.close()
        return jsonify(rendered)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get scheduled follow-ups."""
    try:
        db = Session(engine)
        followups = db.query(ScheduledFollowup).order_by(ScheduledFollowup.scheduled_date).all()

        result = []
        for followup in followups:
            result.append({
                'id': followup.id,
                'contact_id': followup.contact_id,
                'template_id': followup.template_id,
                'scheduled_date': followup.scheduled_date.isoformat() if followup.scheduled_date else None,
                'status': followup.status,
                'created_at': followup.created_at.isoformat() if followup.created_at else None
            })

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Sequence API endpoints

@app.route('/api/sequences', methods=['GET'])
def get_sequences():
    """Get all follow-up sequences."""
    try:
        db = Session(engine)
        sequences = db.query(FollowupSequence).order_by(FollowupSequence.name).all()

        result = []
        for sequence in sequences:
            result.append({
                'id': sequence.id,
                'name': sequence.name,
                'description': sequence.description,
                'platform': sequence.platform,
                'is_active': sequence.is_active,
                'step_count': sequence.step_count,
                'total_duration_days': sequence.total_duration_days,
                'created_at': sequence.created_at.isoformat() if sequence.created_at else None,
                'updated_at': sequence.updated_at.isoformat() if sequence.updated_at else None
            })

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sequences', methods=['POST'])
def create_sequence():
    """Create a new follow-up sequence."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        if not data.get('platform'):
            return jsonify({'error': 'Platform is required'}), 400

        db = Session(engine)

        sequence = FollowupSequence(
            name=data['name'],
            description=data.get('description', ''),
            platform=data['platform'],
            is_active=data.get('is_active', True)
        )

        db.add(sequence)
        db.commit()
        db.refresh(sequence)

        sequence_id = sequence.id
        db.close()

        return jsonify({
            'id': sequence_id,
            'name': sequence.name,
            'description': sequence.description,
            'platform': sequence.platform,
            'is_active': sequence.is_active,
            'step_count': 0,
            'total_duration_days': 0,
            'created_at': sequence.created_at.isoformat() if sequence.created_at else None,
            'updated_at': sequence.updated_at.isoformat() if sequence.updated_at else None
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sequences/<int:sequence_id>', methods=['PUT'])
def update_sequence(sequence_id):
    """Update a follow-up sequence."""
    try:
        data = request.get_json()
        db = Session(engine)

        sequence = db.query(FollowupSequence).filter(FollowupSequence.id == sequence_id).first()
        if not sequence:
            db.close()
            return jsonify({'error': 'Sequence not found'}), 404

        # Update fields
        if 'name' in data:
            sequence.name = data['name']
        if 'description' in data:
            sequence.description = data['description']
        if 'platform' in data:
            sequence.platform = data['platform']
        if 'is_active' in data:
            sequence.is_active = data['is_active']

        sequence.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.close()

        return jsonify({'message': 'Sequence updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sequences/<int:sequence_id>', methods=['DELETE'])
def delete_sequence(sequence_id):
    """Delete a follow-up sequence."""
    try:
        db = Session(engine)

        sequence = db.query(FollowupSequence).filter(FollowupSequence.id == sequence_id).first()
        if not sequence:
            db.close()
            return jsonify({'error': 'Sequence not found'}), 404

        db.delete(sequence)
        db.commit()
        db.close()

        return jsonify({'message': 'Sequence deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sequences/<int:sequence_id>/steps', methods=['GET'])
def get_sequence_steps(sequence_id):
    """Get all steps for a sequence."""
    try:
        db = Session(engine)
        steps = db.query(FollowupSequenceStep).filter(
            FollowupSequenceStep.sequence_id == sequence_id
        ).order_by(FollowupSequenceStep.step_number).all()

        result = []
        for step in steps:
            result.append({
                'id': step.id,
                'sequence_id': step.sequence_id,
                'step_number': step.step_number,
                'delay_days': step.delay_days,
                'template_id': step.template_id,
                'is_active': step.is_active,
                'created_at': step.created_at.isoformat() if step.created_at else None,
                'updated_at': step.updated_at.isoformat() if step.updated_at else None
            })

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sequences/<int:sequence_id>/steps', methods=['POST'])
def create_sequence_step(sequence_id):
    """Create a new step in a sequence."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('step_number'):
            return jsonify({'error': 'Step number is required'}), 400
        if not data.get('delay_days'):
            return jsonify({'error': 'Delay days is required'}), 400
        if not data.get('template_id'):
            return jsonify({'error': 'Template ID is required'}), 400

        db = Session(engine)

        # Check if sequence exists
        sequence = db.query(FollowupSequence).filter(FollowupSequence.id == sequence_id).first()
        if not sequence:
            db.close()
            return jsonify({'error': 'Sequence not found'}), 404

        step = FollowupSequenceStep(
            sequence_id=sequence_id,
            step_number=data['step_number'],
            delay_days=data['delay_days'],
            template_id=data['template_id'],
            is_active=data.get('is_active', True)
        )

        db.add(step)
        db.commit()
        db.refresh(step)

        step_id = step.id
        db.close()

        return jsonify({
            'id': step_id,
            'sequence_id': step.sequence_id,
            'step_number': step.step_number,
            'delay_days': step.delay_days,
            'template_id': step.template_id,
            'is_active': step.is_active,
            'created_at': step.created_at.isoformat() if step.created_at else None,
            'updated_at': step.updated_at.isoformat() if step.updated_at else None
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Settings API endpoints

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all application settings."""
    try:
        db = Session(engine)

        # Get Gmail settings
        gmail_creds = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'gmail'
        ).first()

        # Get Codementor settings
        codementor_creds = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'codementor'
        ).first()

        # Get automation settings (stored as JSON in a special record)
        automation_settings = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'automation'
        ).first()

        result = {
            'gmail': gmail_creds.get_credentials() if gmail_creds else {'email': '', 'app_password': ''},
            'codementor': codementor_creds.get_credentials() if codementor_creds else {'access_token': '', 'refresh_token': ''},
            'automation': automation_settings.get_credentials() if automation_settings else {'enabled': False, 'check_interval': 15, 'max_retries': 3, 'timezone': 'UTC'}
        }

        db.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/gmail', methods=['POST'])
def save_gmail_settings():
    """Save Gmail settings."""
    try:
        data = request.get_json()

        if not data.get('email'):
            return jsonify({'error': 'Gmail email is required'}), 400

        db = Session(engine)

        # Check if Gmail credentials already exist
        gmail_creds = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'gmail'
        ).first()

        if gmail_creds:
            # Update existing
            gmail_creds.credentials = PlatformCredentials.save_credentials({
                'email': data['email'],
                'app_password': data.get('app_password', '')
            })
            gmail_creds.updated_at = datetime.now(timezone.utc)
        else:
            # Create new
            gmail_creds = PlatformCredentials(
                platform='gmail',
                credentials=PlatformCredentials.save_credentials({
                    'email': data['email'],
                    'app_password': data.get('app_password', '')
                })
            )
            db.add(gmail_creds)

        db.commit()
        db.close()

        return jsonify({'message': 'Gmail settings saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/codementor', methods=['POST'])
def save_codementor_settings():
    """Save Codementor settings."""
    try:
        data = request.get_json()

        if not data.get('access_token'):
            return jsonify({'error': 'Access token is required'}), 400

        db = Session(engine)

        # Check if Codementor credentials already exist
        codementor_creds = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'codementor'
        ).first()

        if codementor_creds:
            # Update existing
            codementor_creds.credentials = PlatformCredentials.save_credentials({
                'access_token': data['access_token'],
                'refresh_token': data.get('refresh_token', '')
            })
            codementor_creds.updated_at = datetime.now(timezone.utc)
        else:
            # Create new
            codementor_creds = PlatformCredentials(
                platform='codementor',
                credentials=PlatformCredentials.save_credentials({
                    'access_token': data['access_token'],
                    'refresh_token': data.get('refresh_token', '')
                })
            )
            db.add(codementor_creds)

        db.commit()
        db.close()

        return jsonify({'message': 'Codementor settings saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/automation', methods=['POST'])
def save_automation_settings():
    """Save automation settings."""
    try:
        data = request.get_json()

        db = Session(engine)

        # Check if automation settings already exist
        automation_settings = db.query(PlatformCredentials).filter(
            PlatformCredentials.platform == 'automation'
        ).first()

        if automation_settings:
            # Update existing
            automation_settings.credentials = PlatformCredentials.save_credentials({
                'enabled': data.get('enabled', False),
                'check_interval': data.get('check_interval', 15),
                'max_retries': data.get('max_retries', 3),
                'timezone': data.get('timezone', 'UTC')
            })
            automation_settings.updated_at = datetime.now(timezone.utc)
        else:
            # Create new
            automation_settings = PlatformCredentials(
                platform='automation',
                credentials=PlatformCredentials.save_credentials({
                    'enabled': data.get('enabled', False),
                    'check_interval': data.get('check_interval', 15),
                    'max_retries': data.get('max_retries', 3),
                    'timezone': data.get('timezone', 'UTC')
                })
            )
            db.add(automation_settings)

        db.commit()
        db.close()

        return jsonify({'message': 'Automation settings saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/test/gmail', methods=['POST'])
def test_gmail_connection():
    """Test Gmail connection."""
    try:
        data = request.get_json()

        # TODO: Implement actual Gmail connection test
        # For now, just return success
        return jsonify({'message': 'Gmail connection test successful'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/test/codementor', methods=['POST'])
def test_codementor_connection():
    """Test Codementor connection."""
    try:
        data = request.get_json()

        # TODO: Implement actual Codementor connection test
        # For now, just return success
        return jsonify({'message': 'Codementor connection test successful'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Followupper API is running'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
