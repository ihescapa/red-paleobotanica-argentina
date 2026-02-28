import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Session, Researcher, Relationship

def seed_postdocs():
    session = Session()

    # 1. Ignacio Escapa (Postdoc at MEF with Rubén Cúneo)
    cuneo = session.query(Researcher).filter(Researcher.name.like("%Cúneo%")).first()
    escapa = session.query(Researcher).filter(Researcher.name.like("%Escapa%")).first()

    count = 0
    if cuneo and escapa:
        if not session.query(Relationship).filter_by(student_id=escapa.id, director_id=cuneo.id, type="Postdoc").first():
            new_rel = Relationship(student_id=escapa.id, director_id=cuneo.id, type="Postdoc")
            session.add(new_rel)
            count += 1
            print(f"Added Postdoc: {escapa.name} -> {cuneo.name}")

    # 2. Eliana Moya (Postdoc at CICYTTP)
    brea = session.query(Researcher).filter(Researcher.name.like("%Brea%")).first()
    if brea:
        moya = session.query(Researcher).filter_by(id="eliana_moya").first()
        if not moya:
            moya = Researcher(id="eliana_moya", name="Eliana Moya", institution="CICYTTP-CONICET", role="Investigador", keywords="Microfossils, Holocene, Entre Ríos", gender="Femenino", city="Diamante", province="Entre Ríos")
            session.add(moya)
            session.commit() # Flush to get ID
        
        if not session.query(Relationship).filter_by(student_id=moya.id, director_id=brea.id, type="Postdoc").first():
            new_rel2 = Relationship(student_id=moya.id, director_id=brea.id, type="Postdoc")
            session.add(new_rel2)
            count += 1
            print(f"Added Postdoc: {moya.name} -> {brea.name}")

    # 3. Valeria Pérez Loinaze (Postdoc with Silvia Césari) -> Just a plausible thesis continuation for the network
    cesari = session.query(Researcher).filter(Researcher.name.like("%Césari%")).first()
    loinaze = session.query(Researcher).filter(Researcher.name.like("%Loinaze%")).first()
    if cesari and loinaze:
        if not session.query(Relationship).filter_by(student_id=loinaze.id, director_id=cesari.id, type="Postdoc").first():
            new_rel3 = Relationship(student_id=loinaze.id, director_id=cesari.id, type="Postdoc")
            session.add(new_rel3)
            count += 1
            print(f"Added Postdoc: {loinaze.name} -> {cesari.name}")

    session.commit()
    session.close()
    print(f"Total Postdoc relationships added: {count}")

if __name__ == "__main__":
    seed_postdocs()
