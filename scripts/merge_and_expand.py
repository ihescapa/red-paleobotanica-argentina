from models import Session, Researcher, Relationship

def merge_and_expand():
    session = Session()
    
    # 1. MERGE Ignacio Escapa (ignacio_escapa -> escapa_i)
    # Check if both exist
    escapa_old = session.query(Researcher).filter_by(id="escapa_i").first()
    escapa_new = session.query(Researcher).filter_by(id="ignacio_escapa").first()
    
    if escapa_old and escapa_new:
        print(f"Merging {escapa_new.id} into {escapa_old.id}")
        # Re-assign relationships where ignacio_escapa is director
        rels_director = session.query(Relationship).filter_by(director_id="ignacio_escapa").all()
        for rel in rels_director:
            # Check if this relationship already exists for escapa_i
            existing = session.query(Relationship).filter_by(director_id="escapa_i", student_id=rel.student_id).first()
            if not existing:
                rel.director_id = "escapa_i"
            else:
                session.delete(rel) # Duplicate relationship
        
        # Re-assign relationships where ignacio_escapa is student
        rels_student = session.query(Relationship).filter_by(student_id="ignacio_escapa").all()
        for rel in rels_student:
            existing = session.query(Relationship).filter_by(director_id=rel.director_id, student_id="escapa_i").first()
            if not existing:
                rel.student_id = "escapa_i"
            else:
                session.delete(rel)
        
        # Merge other fields if needed (e.g., Molano was under ignacio_escapa)
        # Molano's relationship was likely moved above.
        
        # Delete the duplicate researcher
        session.delete(escapa_new)
        print("Merge complete.")
    
    # 2. ADD NEW STUDENTS (PhD in progress)
    def get_or_create(id, name, role="Becario", inst=None, is_phd=True):
        r = session.query(Researcher).filter_by(id=id).first()
        if not r:
            r = Researcher(id=id, name=name, role=role, institution=inst, is_phd_in_progress=is_phd)
            session.add(r)
            print(f"Created researcher: {name}")
        else:
            r.is_phd_in_progress = is_phd
        return r

    def add_rel(dir_id, stu_id, type="Primary"):
        # Use merged ID if director is escapa
        if dir_id == "ignacio_escapa": dir_id = "escapa_i"
        
        rel = session.query(Relationship).filter_by(director_id=dir_id, student_id=stu_id).first()
        if not rel:
            session.add(Relationship(director_id=dir_id, student_id=stu_id, type=type))
            print(f"Added relationship: {dir_id} -> {stu_id}")

    # Ignacio Escapa's Students (MEF)
    get_or_create("nadia_woloszyn", "Nadia Mariana Woloszyn", inst="MEF")
    get_or_create("giovanni_nunes", "Giovanni Cristian Nunes", inst="MEF")
    get_or_create("facundo_de_benedetti", "Facundo De Benedetti", inst="MEF") # ensure he's marked as PhD in progress
    get_or_create("maria_savoretti", "María Adolfina Savoretti", inst="MLP") # co-directed
    
    add_rel("escapa_i", "nadia_woloszyn")
    add_rel("escapa_i", "giovanni_nunes")
    add_rel("escapa_i", "facundo_de_benedetti")
    add_rel("escapa_i", "maria_savoretti", type="Secondary")

    # Ari Iglesias's Students (INIBIOMA)
    # Already added Ari and some students, ensuring they are marked correct
    get_or_create("marisol_beltran", "Marisol Beltrán", inst="INIBIOMA")
    get_or_create("eva_silva_bandeira", "Eva M. Silva Bandeira", inst="INIBIOMA")
    
    add_rel("ari_iglesias", "marisol_beltran")
    add_rel("ari_iglesias", "eva_silva_bandeira")

    session.commit()
    session.close()
    print("Expansion complete.")

if __name__ == "__main__":
    merge_and_expand()
