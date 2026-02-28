import sqlite3

def migrate():
    conn = sqlite3.connect('genealogy.db')
    cursor = conn.cursor()
    
    # Add new columns to researchers table
    new_cols = ['scholar_url', 'researchgate_url']
    for col in new_cols:
        try:
            cursor.execute(f"ALTER TABLE researchers ADD COLUMN {col} TEXT")
            print(f"Column '{col}' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column '{col}' already exists.")
            else:
                raise e
    
    # Create publications table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS publications (
                id INTEGER PRIMARY KEY,
                researcher_id TEXT NOT NULL,
                title TEXT NOT NULL,
                year INTEGER,
                journal TEXT,
                citation_count INTEGER,
                url TEXT,
                FOREIGN KEY(researcher_id) REFERENCES researchers(id)
            )
        """)
        print("Table 'publications' created successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error creating table: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
