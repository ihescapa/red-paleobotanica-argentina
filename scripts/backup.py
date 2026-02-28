import shutil
from datetime import datetime
import os
import time

DB_FILE = "genealogy.db"
BACKUP_DIR = "backups"

def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"genealogy_{timestamp}.db")
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    print("Starting Backup Service (Ctrl+C to stop)...")
    while True:
        create_backup()
        # Wait for 24 hours (86400 seconds)
        print("Waiting 24 hours for next backup...")
        time.sleep(86400)
