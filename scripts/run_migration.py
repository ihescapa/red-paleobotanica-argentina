import sqlite3

def migrate():
    conn = sqlite3.connect('genealogy.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE researchers ADD COLUMN photo_url TEXT")
        print("Column 'photo_url' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'photo_url' already exists.")
        else:
            raise e
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
