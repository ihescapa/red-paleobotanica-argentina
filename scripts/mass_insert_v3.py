from models import Session, Researcher, Relationship
from datetime import datetime

def insert_mass_data():
    session = Session()
    user_id = 1
    
    new_researchers = [
        # === CUNEO STUDENTS (MEF) ===
        Researcher(id="de_benedetti_f", name="Facundo De Benedetti", institution="MEF", role="Investigador", notes="Palinología Cretácico-Terciario.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="andruchow_a", name="Ana Andruchow Colombo", institution="MEF", role="Becario", notes="Co-dirigida por Lone Aagesen.", activity_start=2018, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === OTTONE STUDENTS (UBA) ===
        Researcher(id="carrizo_m", name="Martín Carrizo", institution="MACN", role="Investigador", notes="Pteridophyta Cretácico. Co-dirigido por Del Fueyo.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="de_giuseppe_b", name="Bianca De Giuseppe", institution="UBA", role="Becario", notes="Co-dirigida por Ottone.", activity_start=2018, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === GUTIERREZ STUDENTS ===
        Researcher(id="cariglino_b", name="Bárbara Cariglino", institution="UNLP", role="Investigador", notes="Pérmico Cuenca La Golondrina.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === PUJANA STUDENTS ===
        Researcher(id="ruiz_d", name="Daniela Ruiz", institution="MACN", role="Investigador", notes="Maderas fósiles Cretácico-Paleógeno. Co-dirigida por L. Martinez.", activity_start=2010, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === PRAMPARO STUDENTS ===
        Researcher(id="puebla_g", name="Griselda Puebla", institution="IANIGLA", role="Investigador", notes="Evolución vegetación Cretácico-Cenozoico.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === BREA STUDENTS ===
        Researcher(id="beltran_m", name="Marisol Beltrán", institution="CICYTTP", role="Becario", notes="Tesista de M. Brea.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === DI PASQUO STUDENTS ===
        Researcher(id="munoz_n", name="Nadia Muñoz", institution="CICYTTP", role="Becario", notes="Palinología Cuaternario Entre Ríos.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="nunez_n", name="Noelia Nuñez Otaño", institution="CICYTTP", role="Becario", notes="Palinología Cuaternario.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="navarrete_f", name="Francisco Navarrete", institution="Perú", role="Becario", notes="Mioceno-Plioceno Perú.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="perez_e", name="Egly Pérez Pincheira", institution="CICYTTP", role="Becario", notes="Cretácico-Paleoceno Río Negro/Neuquén.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        Researcher(id="quetglas_m", name="Marcela Quetglas", institution="CICYTTP", role="Becario", notes="Megasporias Devónico-Carbonífero.", activity_start=2015, activity_end=2024, created_by=user_id, last_edited_by=user_id),
        
        # === MISSING FORMADORES (need upstream research) ===
        Researcher(id="lutz_a", name="Alicia Lutz", institution="UNNE / CECOAL", role="Investigador Formador", notes="Triásico Marayes. Discípula de Herbst.", activity_start=1980, activity_end=2016, created_by=user_id, last_edited_by=user_id),
        Researcher(id="passalia_m", name="Mauro Passalia", institution="MACN", role="Investigador", notes="Cutículas fósiles. CO2 paleoatmosférico.", activity_start=2005, activity_end=2024, created_by=user_id, last_edited_by=user_id),
    ]

    for r in new_researchers:
        if not session.query(Researcher).filter_by(id=r.id).first():
            session.add(r)
            print(f"✓ {r.name}")
    session.commit()

    relationships = [
        # Cúneo Line
        {"s": "de_benedetti_f", "d": "cuneo_r", "t": "Primary"},
        {"s": "andruchow_a", "d": "escapa_i", "t": "Primary"},
        
        # Ottone Line
        {"s": "carrizo_m", "d": "ottone_e", "t": "Primary"},
        {"s": "carrizo_m", "d": "del_fueyo_g", "t": "Secondary"},
        {"s": "de_giuseppe_b", "d": "ottone_e", "t": "Primary"},
        
        # Gutiérrez Line
        {"s": "cariglino_b", "d": "gutierrez_p", "t": "Primary"},
        
        # Pujana Line
        {"s": "ruiz_d", "d": "pujana_r", "t": "Primary"},
        {"s": "ruiz_d", "d": "martinez_l", "t": "Secondary"},
        
        # Prámparo Line
        {"s": "puebla_g", "d": "pramparo_m", "t": "Primary"},
        
        # Brea Line
        {"s": "beltran_m", "d": "brea_m", "t": "Primary"},
        
        # Di Pasquo Line
        {"s": "munoz_n", "d": "di_pasquo_m", "t": "Primary"},
        {"s": "nunez_n", "d": "di_pasquo_m", "t": "Primary"},
        {"s": "navarrete_f", "d": "di_pasquo_m", "t": "Primary"},
        {"s": "perez_e", "d": "di_pasquo_m", "t": "Primary"},
        {"s": "quetglas_m", "d": "di_pasquo_m", "t": "Primary"},
        
        # Herbst Line (Lutz)
        {"s": "lutz_a", "d": "herbst_r", "t": "Primary"},
    ]

    for rel in relationships:
        if not session.query(Relationship).filter_by(student_id=rel["s"], director_id=rel["d"]).first():
            session.add(Relationship(student_id=rel["s"], director_id=rel["d"], type=rel["t"]))
            print(f"→ {rel['d']} -> {rel['s']}")

    session.commit()
    session.close()
    print(f"\n✅ Inserted {len(new_researchers)} researchers and {len(relationships)} relationships")

if __name__ == "__main__":
    insert_mass_data()
