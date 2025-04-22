import os
from smile_detector.app_config import config, logger


class FSLock:
    """
    A class to handle file system locks using a lock file.
    """

    def __init__(self, lock_file: str) -> None:
        self.lock_file : str = lock_file

    def acquire(self) -> bool:
        """
        Acquire the lock by creating a lock file.
        """
        try:
            with open(self.lock_file, 'w') as f:
                f.write('LOCK')
            logger.info(f"PID={config.pid}; Lock acquired: {self.lock_file}")
            return True
        except FileExistsError:
            logger.debug(f"PID={config.pid}; Lock file already exists: {self.lock_file}")
            return False

    def release(self) -> bool:
        """
        Release the lock by deleting the lock file.
        """
        try:
            os.remove(self.lock_file)
            logger.info(f"PID={config.pid}; Lock released: {self.lock_file}")
            return True
        except FileNotFoundError:
            logger.error(f"PID={config.pid}; Lock file not found for release: {self.lock_file}")
            return False