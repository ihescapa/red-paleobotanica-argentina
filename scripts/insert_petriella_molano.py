from models import Session, Researcher, Relationship

def insert_data():
    session = Session()
    
    # help to get or create researcher
    def get_or_create_researcher(id, name, role="Investigador", inst=None, is_phd=False):
        r = session.query(Researcher).filter_by(id=id).first()
        if not r:
            r = Researcher(id=id, name=name, role=role, institution=inst, is_phd_in_progress=is_phd)
            session.add(r)
            print(f"Created researcher: {name}")
        else:
            r.is_phd_in_progress = is_phd # update if exists
        return r

    def add_rel(dir_id, stu_id, type="Primary"):
        rel = session.query(Relationship).filter_by(director_id=dir_id, student_id=stu_id).first()
        if not rel:
            session.add(Relationship(director_id=dir_id, student_id=stu_id, type=type))
            print(f"Added relationship: {dir_id} -> {stu_id}")

    # Bruno Petriella
    petriella = get_or_create_researcher("bruno_petriella", "Bruno Petriella", "Formador", "MLP")
    add_rel("bruno_petriella", "alba_zamuner")
    
    # Alejandro Molano (PhD student of Ignacio Escapa)
    molano = get_or_create_researcher("alejandro_molano", "Alejandro Molano", "Becario", "MEF", is_phd=True)
    # Ensure Ignacio Escapa exists
    escapa = get_or_create_researcher("ignacio_escapa", "Ignacio Escapa", "Formador", "MEF")
    add_rel("ignacio_escapa", "alejandro_molano")

    session.commit()
    session.close()
    print("Insertion complete.")

if __name__ == "__main__":
    insert_data()
