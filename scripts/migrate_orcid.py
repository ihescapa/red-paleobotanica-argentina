import sqlite3

def migrate():
    conn = sqlite3.connect('genealogy.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE researchers ADD COLUMN orcid_url TEXT")
        print("Column orcid_url added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Column orcid_url might already exist: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
