import os

class FSLock:
    """
    A class to handle file system locks using a lock file.
    """

    def __init__(self, lock_file):
        self.lock_file = lock_file

    def acquire(self):
        """
        Acquire the lock by creating a lock file.
        """
        try:
            with open(self.lock_file, 'x') as f:
                f.write('LOCK')
            return True
        except FileExistsError:
            return False

    def release(self):
        """
        Release the lock by deleting the lock file.
        """
        try:
            os.remove(self.lock_file)
            return True
        except FileNotFoundError:
            return False