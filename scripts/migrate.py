import yaml
from models import Session, Researcher, Relationship, User, engine, Base
from auth import hash_password

# 1. Reset DB
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = Session()

# 2. Create Admin User
admin = User(
    username="admin",
    password_hash=hash_password("admin123"),
    full_name="Sistema",
    institution="Admin"
)
session.add(admin)
session.commit()

# 3. Load YAML
with open("data.yaml", "r") as f:
    data = yaml.safe_load(f)

people = data.get("people", [])

# 4. Migrate Researchers
print("Migrating Researchers...")
for p in people:
    r = Researcher(
        id=p["id"],
        name=p["name"],
        institution=p.get("institution", ""),
        role=p.get("role", "Investigador"),
        notes=p.get("notes", ""),
        created_by=admin.id,
        last_edited_by=admin.id
    )
    session.add(r)
print(f"Added {len(people)} researchers.")

# 5. Migrate Relationships
print("Migrating Relationships...")
count_rel = 0
for p in people:
    student_id = p["id"]
    directors = p.get("directors", [])
    
    for d_id in directors:
        # Verify director exists
        if any(x["id"] == d_id for x in people):
            rel = Relationship(
                student_id=student_id,
                director_id=d_id,
                type="Primary" # Defaulting to Primary for now
            )
            session.add(rel)
            count_rel += 1
        else:
            print(f"Warning: Director ID {d_id} not found for student {student_id}")

print(f"Added {count_rel} relationships.")

session.commit()
session.close()
print("Migration Complete!")
