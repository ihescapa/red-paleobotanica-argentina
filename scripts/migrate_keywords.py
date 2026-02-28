from models import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE researchers ADD COLUMN keywords TEXT"))
            conn.commit()
            print("Successfully added 'keywords' column to researchers table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column 'keywords' already exists.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
