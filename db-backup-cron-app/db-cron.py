import os
import shutil
import datetime
from dotenv import load_dotenv
import subprocess
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pyminizip
import time

# Load environment variables
load_dotenv()

# Configuration
DATABASE = os.getenv("DATABASE", "sqlite").lower()

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# default_dir = os.path.join(BASE_DIR, "db-backups")
BACKUP_DIR = os.getenv("BACKUP_DIR", "./db-backup-cron-app/db-backups")

DRIVE_FOLDER_ID = "1brN7DPFZGp45I_N-zrknZpZ77LjV6RhN"
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
BACKUP_PASSWORD = os.getenv("BACKUP_PASSWORD", "yoko@123")  # Password for encrypted backups
# TIME_INTERVAL = os.getenv("CRON_TIME_INTERVAL", 604800)  # 7 days once by default

def ensure_backup_dir():
    """Ensure backup directory exists"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def get_timestamp():
    """Get current timestamp in format YYYYMMDD_HHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_sqlite():
    """Backup SQLite database"""
    db_path = os.getenv("DATABASE_PATH", "/GarmentCode/data/app.db")
    if not os.path.exists(db_path):
        print("❌ SQLite database not found at:", db_path)
        return None

    ensure_backup_dir()
    backup_file = os.path.join(BACKUP_DIR, f"sqlite_backup_{get_timestamp()}.db")

    try:
        shutil.copy2(db_path, backup_file)
        print(f"✅ SQLite DB backed up to: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ SQLite backup failed: {e}")
        return None

def backup_mysql():
    """Backup MySQL database"""
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DB", "test")

    ensure_backup_dir()
    backup_file = os.path.join(BACKUP_DIR, f"mysql_backup_{get_timestamp()}.sql")

    try:
        with open(backup_file, "w") as out_file:
            subprocess.run(
                [
                    "mysqldump",
                    f"-h{host}",
                    f"-P{port}",
                    f"-u{user}",
                    f"-p{password}",
                    db,
                ],
                stdout=out_file,
                check=True
            )
        print(f"✅ MySQL DB backed up to: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"❌ MySQL backup failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during MySQL backup: {e}")
        return None

def upload_to_drive(file_path):
    """Upload file to Google Drive using service account"""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Service account file not found: {SERVICE_ACCOUNT_FILE}")
        return False

    try:
        # Authenticate using service account
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)

        # Prepare file metadata
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [DRIVE_FOLDER_ID] if DRIVE_FOLDER_ID else []
        }

        # Upload file
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"✅ File uploaded to Google Drive with ID: {file.get('id')}")
        return True

    except Exception as e:
        print(f"❌ Failed to upload to Google Drive: {e}")
        return False

def encrypt_backup_file(file_path):
    """Encrypt the backup file using pyminizip"""
    if not os.path.exists(file_path):
        print(f"❌ Backup file not found: {file_path}")
        return None

    try:
        zip_file = f"{file_path}.zip"
        # Compress and encrypt the file (compression level 5)
        pyminizip.compress(file_path, None, zip_file, BACKUP_PASSWORD, 5)
        print(f"✅ File encrypted and zipped: {zip_file}")
        return zip_file
    except Exception as e:
        print(f"❌ Failed to encrypt backup file: {e}")
        return None

def main():
    """Main backup and upload process"""
    # Perform backup based on database type
    backup_file = backup_mysql() if DATABASE == "mysql" else backup_sqlite()

    if backup_file and os.path.exists(backup_file):
        # Try to encrypt the backup file
        encrypted_file = encrypt_backup_file(backup_file)

        if encrypted_file and os.path.exists(encrypted_file):
            # Upload encrypted file to Google Drive
            if upload_to_drive(encrypted_file):
                # Delete both local files after successful upload
                try:
                    os.remove(backup_file)
                    os.remove(encrypted_file)
                    print(f"✅ Local backup files deleted: {backup_file}, {encrypted_file}")
                except Exception as e:
                    print(f"❌ Failed to delete local backup files: {e}")
        else:
            print("⚠️ Encryption failed, attempting to upload original backup file")
            # Upload original file if encryption failed
            if upload_to_drive(backup_file):
                try:
                    os.remove(backup_file)
                    print(f"✅ Local backup file deleted: {backup_file}")
                except Exception as e:
                    print(f"❌ Failed to delete local backup file: {e}")
    else:
        print("❌ Backup failed, skipping upload")

# def periodic_backup(interval_seconds=60):
#     while True:
#         try:
#             main()
#         except Exception as e:
#             print(f"❌ Backup failed with error: {e}")
#         time.sleep(interval_seconds)

if __name__ == "__main__":
    # interval = int(TIME_INTERVAL)
    # periodic_backup(interval)  # Run every 60 seconds
    main()
