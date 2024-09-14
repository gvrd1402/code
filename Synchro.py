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
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def sync_folders(source, replica, log_file):
    source = Path(source)
    replica = Path(replica)

    if not source.exists() or not source.is_dir():
        logging.error(f"Source folder '{source}' does not exist or is not a directory.")
        return

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
        logging.FileHandler(log_file, mode='a'), logging.StreamHandler()
    ])

    def sync(src_dir, replica_dir):
        if not replica_dir.exists():
            logging.info(f"Creating directory: {replica_dir}")
            replica_dir.mkdir(parents=True)

        for item in src_dir.iterdir():
            src_item = src_dir / item.name
            replica_item = replica_dir / item.name

            if src_item.is_dir():
                sync(src_item, replica_item)
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

        for item in replica_dir.iterdir():
            replica_item = replica_dir / item.name
            src_item = src_dir / item.name
            try:
                if not src_item.exists():
                    if replica_item.is_dir():
                        logging.info(f"Removing directory: {replica_item}")
                        shutil.rmtree(replica_item)
                    else:
                        logging.info(f"Removing file: {replica_item}")
                        replica_item.unlink()
            except Exception as e:
                logging.error(f"Error removing {replica_item}: {e}")

    sync(source, replica)
    logging.info(f"Synchronized {source} to {replica}.")

def main():
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
