from models import Session, Researcher, Relationship

def merge_researchers(source_id, target_id):
    session = Session()
    source = session.query(Researcher).get(source_id)
    target = session.query(Researcher).get(target_id)
    
    if not source or not target:
        print(f"Error: Could not find {source_id} or {target_id}")
        return

    print(f"Merging {source.name} ({source_id}) into {target.name} ({target_id})...")
    
    # Migrate relationships where source is student
    source_stu_rels = session.query(Relationship).filter(Relationship.student_id == source_id).all()
    for rel in source_stu_rels:
        # Check if target already has this relationship
        exists = session.query(Relationship).filter(
            Relationship.student_id == target_id,
            Relationship.director_id == rel.director_id
        ).first()
        
        if not exists:
            rel.student_id = target_id
            print(f"Migrated relationship: {rel.director_id} -> {target_id} ({rel.type})")
        else:
            session.delete(rel)
            print(f"Deleted duplicate relationship: {rel.director_id} -> {source_id}")

    # Migrate relationships where source is director
    source_dir_rels = session.query(Relationship).filter(Relationship.director_id == source_id).all()
    for rel in source_dir_rels:
        exists = session.query(Relationship).filter(
            Relationship.director_id == target_id,
            Relationship.student_id == rel.student_id
        ).first()
        
        if not exists:
            rel.director_id = target_id
            print(f"Migrated relationship (Director): {target_id} -> {rel.student_id} ({rel.type})")
        else:
            session.delete(rel)
            print(f"Deleted duplicate relationship (Director): {source_id} -> {rel.student_id}")

    # Delete source
    session.delete(source)
    session.commit()
    print("Merge complete.")

if __name__ == "__main__":
    # Standardize on cristina_nunez
    merge_researchers('nunes_g', 'cristina_nunez')
