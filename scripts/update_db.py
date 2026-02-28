from models import engine, Base, Suggestion
# Create tables that don't exist
Base.metadata.create_all(engine)
print("Database schema updated with Suggestions table.")
