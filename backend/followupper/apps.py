from django.apps import AppConfig


class FollowupperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "followupper"
    
    def ready(self):
        """Start the scheduler when Django is ready."""
        import sys
        import os
        
        # Don't start scheduler during migrations or other management commands
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        # Only start in the main process (not in reloader subprocess)
        # For Django dev server, RUN_MAIN is set in the reloader
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') != 'true':
                return
        
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            import logging
            logger = logging.getLogger('followupper')
            logger.warning(f"Failed to start scheduler: {e}")