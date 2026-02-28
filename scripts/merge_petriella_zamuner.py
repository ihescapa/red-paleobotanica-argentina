from models import Session, Researcher, Relationship

session = Session()

def merge_researchers(from_id, to_id):
    print(f"Checking merge: {from_id} -> {to_id}")
    r_from = session.query(Researcher).filter_by(id=from_id).first()
    r_to = session.query(Researcher).filter_by(id=to_id).first()
    
    if r_from and r_to:
        print(f"Merging {from_id} into {to_id}")
        
        # Move relationships where from_id is director
        rels_director = session.query(Relationship).filter_by(director_id=from_id).all()
        for rel in rels_director:
            existing = session.query(Relationship).filter_by(director_id=to_id, student_id=rel.student_id).first()
            if not existing:
                rel.director_id = to_id
            else:
                session.delete(rel)
        
        # Move relationships where from_id is student
        rels_student = session.query(Relationship).filter_by(student_id=from_id).all()
        for rel in rels_student:
            existing = session.query(Relationship).filter_by(director_id=rel.director_id, student_id=to_id).first()
            if not existing:
                rel.student_id = to_id
            else:
                session.delete(rel)
        
        # Delete the duplicate researcher
        session.delete(r_from)
        print(f"Merge of {from_id} complete.")
    else:
        if not r_from: print(f"Researcher {from_id} not found")
        if not r_to: print(f"Researcher {to_id} not found")

# Merge Zamuners
merge_researchers('alba_zamuner', 'zamuner_a')

# Merge Petriellas
merge_researchers('bruno_petriella', 'petriella_b')

# Final check for relationship
p = session.query(Researcher).filter_by(id='petriella_b').first()
z = session.query(Researcher).filter_by(id='zamuner_a').first()

if p and z:
    rel = session.query(Relationship).filter_by(director_id=p.id, student_id=z.id).first()
    if not rel:
        session.add(Relationship(director_id=p.id, student_id=z.id, type='Primary'))
        print(f"Added relationship: {p.name} -> {z.name}")
    else:
        print(f"Relationship already exists: {p.id} -> {z.id}")

session.commit()
session.close()
