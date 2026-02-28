from models import Session, Relationship, Researcher

def update_lineage_and_years():
    session = Session()
    
    # 1. Add Artabe - Petriella relationship
    # Check if already exists
    exists = session.query(Relationship).filter(
        Relationship.student_id == 'artabe_a',
        Relationship.director_id == 'petriella_b'
    ).first()
    
    if not exists:
        session.add(Relationship(student_id='artabe_a', director_id='petriella_b', type='Primary'))
        print("Added relationship: Petriella -> Artabe")
    else:
        print("Relationship Petriella -> Artabe already exists.")

    # 2. Update Activity Years (Estimates)
    updates = {
        'archangelsky_s': (1963, 2022),
        'petriella_b': (1965, 1995), # Estimated end
        'artabe_a': (1978, 2023), # Estimated start/active
        'cuneo_r': (1985, 2024), # Estimated start
        'escapa_i': (2008, 2024),
        'iglesias_a': (2007, 2024),
        'zucol_a': (1990, 2024),
        'brea_m': (1995, 2024),
        'lutz_a': (1980, 2020),
        'anzotegui_l': (1980, 2020),
        'crisafulli_a': (1985, 2024),
        'del_fueyo_g': (1985, 2024),
    }
    
    for rid, (start, end) in updates.items():
        r = session.query(Researcher).get(rid)
        if r:
            r.activity_start = start
            r.activity_end = end
            print(f"Updated {r.name}: {start}-{end}")
        else:
            print(f"Researcher {rid} not found for year update.")

    session.commit()
    session.close()
    print("Update complete.")

if __name__ == "__main__":
    update_lineage_and_years()
