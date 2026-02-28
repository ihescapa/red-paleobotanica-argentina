from models import Session, Researcher, Relationship
from datetime import datetime

def insert_ultra_deep():
    session = Session()
    user_id = 1
    
    new_researchers = [
        # === ZAVATTIERI LINE ===
        Researcher(id="zavattieri_am", name="Ana María Zavattieri", institution="IANIGLA - CONICET", role="Investigador Formador", notes="Triásico. Directores: Martino/Ramos.", activity_start=1990, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="olivera_d", name="Daniela Olivera", institution="INGEOSUR - CONICET", role="Investigador", notes="Palinología Jurásico. Co-dir: Quattrocchio.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === ARCHANGELSKY STUDENTS (Missing) ===
        Researcher(id="petriella_b", name="Bruno Petriella", institution="UNLP", role="Investigador Formador", notes="Maderas petrificadas Terciario. Fallecido 1984.", activity_start=1965, activity_end=1984, created_by=user_id, last_edited_by=user_id),
        
        # === INDEPENDENT FORMADORES ===
        Researcher(id="galli_c", name="Claudia Galli", institution="UNSa - CONICET", role="Investigador Formador", notes="Mioceno tardío NO Argentina.", activity_start=1995, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="llorens_m", name="Magdalena Llorens", institution="MEF - CONICET", role="Investigador", notes="Palinología Cretácico. Divulgación.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
    ]

    for r in new_researchers:
        if not session.query(Researcher).filter_by(id=r.id).first():
            session.add(r)
            print(f"✓ {r.name}")
    session.commit()

    relationships = [
        # Zavattieri Line
        {"s": "olivera_d", "d": "zavattieri_am", "t": "Primary"},
        {"s": "olivera_d", "d": "quattrocchio_m", "t": "Secondary"},
        
        # Archangelsky Line
        {"s": "petriella_b", "d": "archangelsky_s", "t": "Primary"},
    ]

    for rel in relationships:
        if not session.query(Relationship).filter_by(student_id=rel["s"], director_id=rel["d"]).first():
            session.add(Relationship(student_id=rel["s"], director_id=rel["d"], type=rel["t"]))
            print(f"→ {rel['d']} -> {rel['s']}")

    session.commit()
    session.close()
    print(f"\n✅ Ultra-deep batch complete!")

if __name__ == "__main__":
    insert_ultra_deep()
