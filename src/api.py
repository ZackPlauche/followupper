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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Followupper API is running'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
