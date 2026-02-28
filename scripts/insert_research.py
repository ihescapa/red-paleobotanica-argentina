from models import Session, Researcher, Relationship, AuditLog, User
from datetime import datetime

def insert_data():
    session = Session()
    user_id = 1 # Admin
    
    # New Researchers
    new_researchers = [
        Researcher(
            id="palazzesi_l",
            name="Luis Palazzesi",
            institution="MACN - CONICET",
            role="Investigador Formador",
            notes="Palinología. Especialista en climas del pasado (Patagonia/Antártida).",
            activity_start=2000,
            activity_end=2024,
            created_by=user_id,
            last_edited_by=user_id
        ),
        Researcher(
            id="fernandez_d",
            name="Damián Fernández",
            institution="CADIC - CONICET",
            role="Investigador",
            notes="Palinología del Paleógeno (Tierra del Fuego).",
            activity_start=2010,
            activity_end=2024,
            created_by=user_id,
            last_edited_by=user_id
        ),
        Researcher(
            id="scafati_l",
            name="Laura Scafati",
            institution="MACN - CONICET",
            role="Investigador",
            notes="Palinología. Colaboradora histórica del grupo Volkheimer.",
            activity_start=1990,
            activity_end=2020,
            created_by=user_id,
            last_edited_by=user_id
        ),
        Researcher(
            id="cornou_m",
            name="María Elina Cornou",
            institution="UNS - CONICET",
            role="Investigador",
            notes="Discípula de M. Quattrocchio.",
            activity_start=2005,
            activity_end=2024,
            created_by=user_id,
            last_edited_by=user_id
        ),
        Researcher(
            id="aguero_l",
            name="Luis Sebastián Agüero",
            institution="UNS",
            role="Investigador",
            notes="Colaborador/Tesista de M. Quattrocchio.",
            activity_start=2010,
            activity_end=2024,
            created_by=user_id,
            last_edited_by=user_id
        ),
        Researcher(
            id="diaz_p",
            name="Pablo Esteban Díaz",
            institution="UNS",
            role="Investigador",
            notes="Grupo de M. Quattrocchio.",
            activity_start=2010,
            activity_end=2024,
            created_by=user_id,
            last_edited_by=user_id
        )
    ]

    # Insert Researchers if not exist
    for r in new_researchers:
        existing = session.query(Researcher).filter_by(id=r.id).first()
        if not existing:
            session.add(r)
            print(f"Added {r.name}")
        else:
            print(f"Skipped {r.name} (Exists)")
    
    session.commit()

    # Relationships
    relationships = [
        # Barreda -> Palazzesi (Primary)
        {"s": "palazzesi_l", "d": "barreda_v", "t": "Primary"},
        # Palazzesi -> Fernández (Primary)
        {"s": "fernandez_d", "d": "palazzesi_l", "t": "Primary"},
        # Barreda -> Fernández (Secondary - Official Director)
        {"s": "fernandez_d", "d": "barreda_v", "t": "Secondary"},
        
        # Volkheimer -> Scafati (Secondary/Collab)
        {"s": "scafati_l", "d": "volkheimer_w", "t": "Secondary"},
        
        # Quattrocchio -> Students
        {"s": "cornou_m", "d": "quattrocchio_m", "t": "Primary"},
        {"s": "aguero_l", "d": "quattrocchio_m", "t": "Primary"},
        {"s": "diaz_p", "d": "quattrocchio_m", "t": "Primary"},
    ]

    for rel in relationships:
        existing = session.query(Relationship).filter_by(student_id=rel["s"], director_id=rel["d"]).first()
        if not existing:
            new_rel = Relationship(student_id=rel["s"], director_id=rel["d"], type=rel["t"])
            session.add(new_rel)
            print(f"Added Rel: {rel['d']} -> {rel['s']}")
        else:
            print(f"Rel Exists: {rel['d']} -> {rel['s']}")

    session.commit()
    session.close()

if __name__ == "__main__":
    insert_data()
