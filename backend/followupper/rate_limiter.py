"""
Rate limiter for Codementor message sending.
Manages concurrent sends and intervals between batches.
"""
import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger('followupper')


class CodementorRateLimiter:
    """Singleton rate limiter for Codementor messages."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.active_sends = 0
        self.current_batch_start_time = None  # When the current batch started
        self.batch_complete_time = None  # When the last batch completed
        self.condition = threading.Condition(self._lock)

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def wait_for_slot(self, max_concurrent, send_interval):
        """Wait until a slot is available for sending.

        Args:
            max_concurrent: Maximum number of concurrent sends allowed
            send_interval: Minimum interval in seconds between batches
        """
        now = datetime.now()
        logger.info(
            f"[RATE_LIMITER] wait_for_slot called at {now} - max_concurrent={max_concurrent}, send_interval={send_interval}, active_sends={
                self.active_sends}, batch_start={
                self.current_batch_start_time}, batch_complete={
                self.batch_complete_time}")

        with self.condition:
            # FIRST: Check if we need to wait for interval since last batch completed
            # This must happen BEFORE checking active_sends to prevent race conditions
            if self.batch_complete_time and self.active_sends == 0:
                time_since_complete = (datetime.now() - self.batch_complete_time).total_seconds()
                logger.info(f"[RATE_LIMITER] Last batch completed {time_since_complete:.2f}s ago, need {send_interval}s interval")
                if time_since_complete < send_interval:
                    wait_time = send_interval - time_since_complete
                    logger.info(f"[RATE_LIMITER] Waiting {wait_time:.2f} seconds before starting new batch...")
                    time.sleep(wait_time)
                    logger.info(f"[RATE_LIMITER] Wait complete, can start new batch")
                # Clear batch_complete_time after waiting
                self.batch_complete_time = None

            # SECOND: Wait if we're at max concurrent (shouldn't happen often, but safety check)
            while self.active_sends >= max_concurrent:
                logger.warning(f"[RATE_LIMITER] At max concurrent ({max_concurrent}), waiting for slot to free up...")
                self.condition.wait()

            # THIRD: If this is the first in a new batch, record the batch start time
            if self.active_sends == 0:
                self.current_batch_start_time = datetime.now()
                logger.info(f"[RATE_LIMITER] Starting new batch at {self.current_batch_start_time}")

            # FOURTH: Acquire slot (we're under max_concurrent)
            self.active_sends += 1
            logger.info(f"[RATE_LIMITER] Slot acquired - active_sends now={self.active_sends}/{max_concurrent}")

    def release_slot(self):
        """Release a slot after sending is complete."""
        with self.condition:
            if self.active_sends > 0:
                self.active_sends -= 1
            logger.info(f"[RATE_LIMITER] Slot released at {datetime.now()} - active_sends now={self.active_sends}, batch_start={self.current_batch_start_time}")

            # If this was the last message in the batch, record completion time
            if self.active_sends == 0 and self.current_batch_start_time:
                self.batch_complete_time = datetime.now()
                logger.info(f"[RATE_LIMITER] Batch completed at {self.batch_complete_time} (started at {self.current_batch_start_time})")

            # Notify waiting threads that a slot might be available
            self.condition.notify_all()
