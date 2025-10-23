"""Follow-up scheduling system using APScheduler."""

from ..models.message_template import MessageTemplate
from ..models.scheduled_followup import ScheduledFollowup
from ..models.contact import Contact
from ..models.database import get_db, engine
from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging
from datetime import datetime, timedelta, timezone


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FollowupScheduler:
    """Manages automated follow-up scheduling."""

    def __init__(self):
        self.scheduler = None
        self.setup_scheduler()

    def setup_scheduler(self):
        """Set up the APScheduler with SQLAlchemy job store."""
        jobstores = {
            'default': SQLAlchemyJobStore(url=str(engine.url))
        }

        executors = {
            'default': ThreadPoolExecutor(max_workers=10)
        }

        job_defaults = {
            'coalesce': True,
            'max_instances': 1
        }

        self.scheduler = QtScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )

        # Add event listeners
        self.scheduler.add_listener(self.job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_error, EVENT_JOB_ERROR)

        self.scheduler.start()
        logger.info("Follow-up scheduler started")

    def schedule_followup(self, contact_id, template_id, scheduled_date, platform):
        """Schedule a follow-up message."""
        try:
            db = next(get_db())

            # Create scheduled follow-up record
            followup = ScheduledFollowup(
                contact_id=contact_id,
                template_id=template_id,
                scheduled_date=scheduled_date,
                platform=platform,
                status='pending'
            )
            db.add(followup)
            db.commit()

            # Schedule the job
            job_id = f"followup_{followup.id}"
            self.scheduler.add_job(
                func=self.send_followup,
                trigger=DateTrigger(run_date=scheduled_date),
                args=[followup.id],
                id=job_id,
                name=f"Follow-up for contact {contact_id}",
                replace_existing=True
            )

            logger.info(f"Scheduled follow-up {followup.id} for {scheduled_date}")
            return followup.id

        except Exception as e:
            logger.error(f"Failed to schedule follow-up: {e}")
            raise

    def send_followup(self, followup_id):
        """Send a scheduled follow-up message."""
        try:
            db = next(get_db())
            followup = db.query(ScheduledFollowup).filter(
                ScheduledFollowup.id == followup_id
            ).first()

            if not followup:
                logger.error(f"Follow-up {followup_id} not found")
                return

            contact = followup.contact
            template = followup.template

            if not contact or not template:
                logger.error(f"Missing contact or template for follow-up {followup_id}")
                followup.status = 'failed'
                followup.error_message = "Missing contact or template"
                db.commit()
                return

            # Update follow-up status
            followup.status = 'sent'
            followup.sent_date = datetime.now(timezone.utc)
            contact.last_contact_date = datetime.now(timezone.utc)

            db.commit()

            # TODO: Actually send the message via Gmail/Codementor API
            logger.info(f"Follow-up {followup_id} sent successfully")

        except Exception as e:
            logger.error(f"Failed to send follow-up {followup_id}: {e}")
            try:
                db = next(get_db())
                followup = db.query(ScheduledFollowup).filter(
                    ScheduledFollowup.id == followup_id
                ).first()
                if followup:
                    followup.status = 'failed'
                    followup.error_message = str(e)
                    followup.retry_count += 1
                    db.commit()
            except BaseException:
                pass

    def schedule_automatic_followups(self):
        """Schedule automatic follow-ups for all active contacts."""
        try:
            db = next(get_db())
            contacts = db.query(Contact).filter(Contact.is_active == True).all()

            for contact in contacts:
                # Check if contact needs a follow-up
                if self.should_schedule_followup(contact):
                    self.schedule_contact_followup(contact)

            logger.info(f"Processed {len(contacts)} contacts for automatic follow-ups")

        except Exception as e:
            logger.error(f"Failed to schedule automatic follow-ups: {e}")

    def should_schedule_followup(self, contact):
        """Check if a contact needs a follow-up scheduled."""
        if not contact.last_contact_date:
            return True

        next_followup = contact.last_contact_date + timedelta(days=contact.follow_up_frequency)
        return datetime.now(timezone.utc) >= next_followup

    def schedule_contact_followup(self, contact):
        """Schedule a follow-up for a specific contact."""
        try:
            db = next(get_db())

            # Get default template for the contact's preferred platform
            template = db.query(MessageTemplate).filter(
                MessageTemplate.platform == contact.platform_preference,
                MessageTemplate.is_default == True,
                MessageTemplate.is_active == True
            ).first()

            if not template:
                logger.warning(f"No default template found for platform {contact.platform_preference}")
                return

            # Schedule for immediate sending (or next available time)
            scheduled_date = datetime.now(timezone.utc) + timedelta(minutes=1)

            self.schedule_followup(
                contact.id,
                template.id,
                scheduled_date,
                contact.platform_preference
            )

        except Exception as e:
            logger.error(f"Failed to schedule follow-up for contact {contact.id}: {e}")

    def get_pending_followups(self):
        """Get all pending follow-ups."""
        try:
            db = next(get_db())
            return db.query(ScheduledFollowup).filter(
                ScheduledFollowup.status == 'pending'
            ).all()
        except Exception as e:
            logger.error(f"Failed to get pending follow-ups: {e}")
            return []

    def get_overdue_followups(self):
        """Get all overdue follow-ups."""
        try:
            db = next(get_db())
            return db.query(ScheduledFollowup).filter(
                ScheduledFollowup.status == 'pending',
                ScheduledFollowup.scheduled_date < datetime.now(timezone.utc)
            ).all()
        except Exception as e:
            logger.error(f"Failed to get overdue follow-ups: {e}")
            return []

    def retry_failed_followups(self):
        """Retry failed follow-ups."""
        try:
            db = next(get_db())
            failed_followups = db.query(ScheduledFollowup).filter(
                ScheduledFollowup.status == 'failed',
                ScheduledFollowup.retry_count < 3
            ).all()

            for followup in failed_followups:
                # Reschedule with exponential backoff
                retry_delay = 2 ** followup.retry_count  # 1, 2, 4 minutes
                scheduled_date = datetime.now(timezone.utc) + timedelta(minutes=retry_delay)

                self.schedule_followup(
                    followup.contact_id,
                    followup.template_id,
                    scheduled_date,
                    followup.platform
                )

                logger.info(f"Retrying follow-up {followup.id} in {retry_delay} minutes")

        except Exception as e:
            logger.error(f"Failed to retry failed follow-ups: {e}")

    def job_executed(self, event):
        """Handle successful job execution."""
        logger.info(f"Job {event.job_id} executed successfully")

    def job_error(self, event):
        """Handle job execution errors."""
        logger.error(f"Job {event.job_id} failed: {event.exception}")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Follow-up scheduler shutdown")
