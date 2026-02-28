from models import Session, Researcher, Relationship

session = Session()
zamuners = session.query(Researcher).filter(Researcher.name.like('%Zamuner%')).all()
for z in zamuners:
    print(f"Researcher: {z.name} (ID: {z.id})")
    rels = session.query(Relationship).filter_by(student_id=z.id).all()
    for r in rels:
        director = session.query(Researcher).filter_by(id=r.director_id).first()
        dir_name = director.name if director else "Unknown"
        print(f"  Directed by: {dir_name} (ID: {r.director_id})")

session.close()
