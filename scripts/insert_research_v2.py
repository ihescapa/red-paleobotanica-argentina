from models import Session, Researcher, Relationship, AuditLog, User
from datetime import datetime

def insert_data():
    session = Session()
    user_id = 1 # Admin
    
    # New Researchers
    new_researchers = [
        # Formadores
        Researcher(id="zamuner_a", name="Alba Zamuner", institution="UNLP", role="Investigador Formador", notes="Experta en floras triásicas y xilología.", activity_start=1980, activity_end=2012, created_by=user_id, last_edited_by=user_id),
        Researcher(id="cesari_s", name="Silvia Césari", institution="MACN - CONICET", role="Investigador Formador", notes="Paleozoico superior. Palinología.", activity_start=1980, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # Césari Students
        Researcher(id="vera_e", name="Ezequiel Vera", institution="MACN", role="Investigador", notes="Anatomía vegetal. Antártida/Patagonia.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="perez_loinaze_v", name="Valeria Pérez Loinaze", institution="MACN", role="Investigador", notes="Palinología.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="pujana_r", name="Roberto Pujana", institution="MACN", role="Investigador", notes="Xilología. Maderas fósiles.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),

        # Zamuner Students
        Researcher(id="iglesias_a", name="Ari Iglesias", institution="INIBIOMA - CONICET", role="Investigador", notes="Paleofloras del Paleoceno/Eoceno.", activity_start=2000, activity_end=2024, created_by=user_id, last_edited_by=user_id),

        # Barreda Students
        Researcher(id="panti_c", name="Carolina Panti", institution="MACN", role="Investigador", notes="Palinología.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),

        # Del Fueyo Students
        Researcher(id="lafuente_diaz_m", name="Maiten Lafuente Diaz", institution="MACN", role="Investigador", notes="Cutículas/Morfología.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),

        # Artabe Students
        Researcher(id="martinez_l", name="Leandro Martínez", institution="UNLP / CONICET", role="Investigador", notes="Xilología Cretácico.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),

        # Bodnar Students
        Researcher(id="procopio_j", name="Jano Nehuén Procopio", institution="UNLP", role="Becario", notes="Tesista de J. Bodnar.", activity_start=2018, activity_end=2024, created_by=user_id, last_edited_by=user_id),
    ]

    # Insert Researchers
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
        # Zamuner Line
        {"s": "iglesias_a", "d": "zamuner_a", "t": "Primary"},
        
        # Césari Line
        {"s": "vera_e", "d": "cesari_s", "t": "Primary"},
        {"s": "perez_loinaze_v", "d": "cesari_s", "t": "Primary"},
        {"s": "pujana_r", "d": "cesari_s", "t": "Primary"},
        
        # Barreda Line
        {"s": "panti_c", "d": "barreda_v", "t": "Primary"},
        
        # Del Fueyo Line
        {"s": "lafuente_diaz_m", "d": "del_fueyo_g", "t": "Primary"},
        
        # Artabe Line
        {"s": "martinez_l", "d": "artabe_a", "t": "Primary"},
        
        # Bodnar Line
        {"s": "procopio_j", "d": "bodnar_j", "t": "Primary"},
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
