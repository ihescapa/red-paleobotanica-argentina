from models import Session, Researcher, Relationship
from datetime import datetime

def insert_final_batch():
    session = Session()
    user_id = 1
    
    new_researchers = [
        # === BODNAR STUDENTS ===
        Researcher(id="coturel_e", name="Eliana Coturel", institution="UNLP", role="Investigador", notes="Co-dirigida por Bodnar.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === ZAMUNER STUDENTS (Additional) ===
        Researcher(id="sagasti_a", name="Ana Julia Sagasti", institution="UNLP", role="Investigador", notes="Jurásico Laguna Flecha Negra. Dir: García Massini.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === ESCAPA STUDENTS (Additional - Cristina Nunez already listed as nunes_c, updating) ===
        # Cristina Nunez = nunes_c (already in DB, co-directed by García Massini)
        
        # === MISSING FORMADORES ===
        Researcher(id="garcia_massini_j", name="Juan García Massini", institution="CRILAR - CONICET", role="Investigador Formador", notes="Paleofloras Jurásicas. Co-director múltiples tesis.", activity_start=2000, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="zamaloa_mc", name="María del Carmen Zamaloa", institution="MEF - CONICET", role="Investigador Formador", notes="Palinología. Co-directora De Benedetti.", activity_start=1995, activity_end=2024, created_by=user_id, last_edited_by=user_id),
    ]

    for r in new_researchers:
        if not session.query(Researcher).filter_by(id=r.id).first():
            session.add(r)
            print(f"✓ {r.name}")
    session.commit()

    relationships = [
        # Bodnar Line
        {"s": "coturel_e", "d": "bodnar_j", "t": "Primary"},
        
        # García Massini Line
        {"s": "sagasti_a", "d": "garcia_massini_j", "t": "Primary"},
        {"s": "nunes_c", "d": "garcia_massini_j", "t": "Secondary"},  # Co-director with Escapa
        
        # Zamaloa Line
        {"s": "de_benedetti_f", "d": "zamaloa_mc", "t": "Secondary"},  # Co-director with Cúneo
    ]

    for rel in relationships:
        if not session.query(Relationship).filter_by(student_id=rel["s"], director_id=rel["d"]).first():
            session.add(Relationship(student_id=rel["s"], director_id=rel["d"], type=rel["t"]))
            print(f"→ {rel['d']} -> {rel['s']}")

    session.commit()
    session.close()
    print(f"\n✅ Final batch complete!")

if __name__ == "__main__":
    insert_final_batch()
