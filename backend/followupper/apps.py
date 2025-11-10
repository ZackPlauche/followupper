from django.apps import AppConfig
import threading
import sys
import os


class FollowupperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "followupper"
    
    def ready(self):
        """Start the scheduler when Django is ready."""
        # Don't start scheduler during migrations or other management commands
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv or 'createsuperuser' in sys.argv:
            return
        
        # Only start in the main process (not in reloader subprocess)
        # For Django dev server, RUN_MAIN is set in the reloader
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') != 'true':
                return
        
        # Defer scheduler start to avoid database access during app initialization
        # Use a thread with a small delay to ensure Django is fully initialized
        def delayed_start():
            import time
            time.sleep(1)  # Wait 1 second for Django to fully initialize
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                import logging
                logger = logging.getLogger('followupper')
                logger.warning(f"Failed to start scheduler: {e}")
        
        thread = threading.Thread(target=delayed_start, daemon=True)
        thread.start()