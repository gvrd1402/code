import os
import shutil
import hashlib
import time
import logging
from pathlib import Path

# hardcoded paths, interval and log
SOURCE_FOLDER = 'C:/Users/jnkuz/OneDrive/Desktop/source'  # Path to the source folder
REPLICA_FOLDER = 'C:/Users/jnkuz/OneDrive/Desktop/replica'  # Path to the replica folder
LOG_FILE = 'C:/Users/jnkuz/OneDrive/Desktop/log.log.log'  # Path to the log file
SYNC_INTERVAL = 5  # Synchronization interval in seconds

def calculate_md5(file_path):
    """Calculate MD5 checksum for a given file."""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def sync_folders(source, replica, log_file):
    """
    Synchronize the contents of the source folder with the replica folder.
    """
    source = Path(source)
    replica = Path(replica)

    if not source.exists() or not source.is_dir():
        logging.error(f"Source folder '{source}' does not exist or is not a directory.")
        return

    # Setup logging - we configure the logging only once to avoid multiple log entries.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
        logging.FileHandler(log_file, mode='a'), logging.StreamHandler()
    ])

    def sync(src_dir, replica_dir):
        # Ensure replica folder exists
        if not replica_dir.exists():
            logging.info(f"Creating directory: {replica_dir}")
            replica_dir.mkdir(parents=True)

        # Get all files and folders in the source directory
        for item in src_dir.iterdir():
            src_item = src_dir / item.name
            replica_item = replica_dir / item.name

            # If the item is a directory, recursively synchronize it
            if src_item.is_dir():
                sync(src_item, replica_item)
            # If it's a file, copy it to the replica if it doesn't exist or is different
            elif src_item.is_file():
                try:
                    if not replica_item.exists():
                        logging.info(f"Copying file: {src_item} to {replica_item}")
                        shutil.copy2(src_item, replica_item)
                    elif calculate_md5(src_item) != calculate_md5(replica_item):
                        logging.info(f"Updating file: {src_item} to {replica_item}")
                        shutil.copy2(src_item, replica_item)
                except Exception as e:
                    logging.error(f"Error copying file {src_item}: {e}")

        # Remove any items from the replica that are not in the source
        for item in replica_dir.iterdir():
            replica_item = replica_dir / item.name
            src_item = src_dir / item.name
            try:
                if not src_item.exists():
                    # If it's a directory, remove it recursively
                    if replica_item.is_dir():
                        logging.info(f"Removing directory: {replica_item}")
                        shutil.rmtree(replica_item)
                    # If it's a file, remove it
                    else:
                        logging.info(f"Removing file: {replica_item}")
                        replica_item.unlink()
            except Exception as e:
                logging.error(f"Error removing {replica_item}: {e}")

    # Start synchronization
    sync(source, replica)
    logging.info(f"Synchronized {source} to {replica}.")

def main():
    # Use hardcoded configurations for source folder, replica folder, and log file
    source_folder = SOURCE_FOLDER
    replica_folder = REPLICA_FOLDER
    log_file = LOG_FILE
    interval = SYNC_INTERVAL

    while True:
        try:
            sync_folders(source_folder, replica_folder, log_file)
        except Exception as e:
            logging.error(f"Error during synchronization: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
