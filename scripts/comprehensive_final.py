from models import Session, Researcher, Relationship
from datetime import datetime

def insert_comprehensive_final():
    session = Session()
    user_id = 1
    
    new_researchers = [
        # === GNAEDINGER STUDENTS ===
        Researcher(id="ribeiro_r", name="Rodrigo Villa Lelis Ribeiro", institution="CECOAL - CONICET", role="Becario", notes="Tesista de Gnaedinger.", activity_start=2018, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="gomez_g", name="Graciela Gómez", institution="CECOAL - CONICET", role="Becario", notes="Tesista de Gnaedinger.", activity_start=2018, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === INDEPENDENT RESEARCHERS (Collaborators) ===
        Researcher(id="monti_m", name="Mariana Monti", institution="CIG - UNLP", role="Investigador", notes="Triásico Mendoza. Palinología.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),
    ]

    for r in new_researchers:
        if not session.query(Researcher).filter_by(id=r.id).first():
            session.add(r)
            print(f"✓ {r.name}")
    session.commit()

    relationships = [
        # Gnaedinger Line
        {"s": "ribeiro_r", "d": "gnaedinger_s", "t": "Primary"},
        {"s": "gomez_g", "d": "gnaedinger_s", "t": "Primary"},
    ]

    for rel in relationships:
        if not session.query(Relationship).filter_by(student_id=rel["s"], director_id=rel["d"]).first():
            session.add(Relationship(student_id=rel["s"], director_id=rel["d"], type=rel["t"]))
            print(f"→ {rel['d']} -> {rel['s']}")

    session.commit()
    session.close()
    print(f"\n✅ Comprehensive research complete!")

if __name__ == "__main__":
    insert_comprehensive_final()
