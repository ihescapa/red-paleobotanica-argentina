from models import Session, Researcher, Relationship, Publication, AuditLog
import sys

def merge_researchers(source_id, target_id):
    session = Session()
    source = session.query(Researcher).get(source_id)
    target = session.query(Researcher).get(target_id)
    
    if not source or not target:
        print(f"Error: One or both researchers not found ({source_id} -> {target_id})")
        session.close()
        return

    print(f"Merging {source_id} ({source.name}) into {target_id} ({target.name})...")
    
    # 1. Update Relationships where source is Director
    rels_as_dir = session.query(Relationship).filter_by(director_id=source_id).all()
    for rel in rels_as_dir:
        # Check if target already has this relationship to avoid unique constraint issues if any
        exists = session.query(Relationship).filter_by(director_id=target_id, student_id=rel.student_id).first()
        if not exists:
            rel.director_id = target_id
        else:
            session.delete(rel)
            
    # 2. Update Relationships where source is Student
    rels_as_stu = session.query(Relationship).filter_by(student_id=source_id).all()
    for rel in rels_as_stu:
        exists = session.query(Relationship).filter_by(student_id=target_id, director_id=rel.director_id).first()
        if not exists:
            rel.student_id = target_id
        else:
            session.delete(rel)

    # 3. Update Publications
    pubs = session.query(Publication).filter_by(researcher_id=source_id).all()
    for pub in pubs:
        pub.researcher_id = target_id

    # 4. Transfer metadata if target is missing it
    if not target.scholar_url and source.scholar_url: target.scholar_url = source.scholar_url
    if not target.researchgate_url and source.researchgate_url: target.researchgate_url = source.researchgate_url
    if not target.orcid_url and hasattr(source, 'orcid_url') and source.orcid_url: target.orcid_url = source.orcid_url
    if not target.photo_url and source.photo_url: target.photo_url = source.photo_url
    if not target.notes and source.notes: target.notes = source.notes
    
    # 5. Delete source
    session.delete(source)
    
    try:
        session.commit()
        print(f"Successfully merged {source_id} into {target_id}")
    except Exception as e:
        session.rollback()
        print(f"Failed to merge {source_id} into {target_id}: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Merge list: source_id, target_id
    merges = [
        ('beltran_m', 'marisol_beltran'),
        ('woloszyn_n', 'nadia_woloszyn'),
        ('archangelsky_s', 'sergio_archangelsky'),
        ('villa_r', 'ribeiro_r')
    ]
    for src, tgt in merges:
        merge_researchers(src, tgt)
