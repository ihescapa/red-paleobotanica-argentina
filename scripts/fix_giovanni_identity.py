from models import Session, Researcher, Relationship, AuditLog, Suggestion

def fix_giovanni():
    session = Session()
    
    # 1. Handle cristina_nunez record
    c_nunez = session.query(Researcher).get('cristina_nunez')
    if not c_nunez:
        print("Error: cristina_nunez not found.")
        return

    print(f"Transforming {c_nunez.name} into Giovanni Nunes...")
    
    # Check if giovanni_nunes already exists (unlikely if merge was clean)
    g_nunes = session.query(Researcher).get('giovanni_nunes')
    if not g_nunes:
        # We need to change the primary key. SQLAlchemy doesn't like PK updates.
        # So we create a new one and migrate relationships.
        g_nunes = Researcher(
            id='giovanni_nunes',
            name="Giovanni Nunes",
            institution=c_nunez.institution,
            role="Investigador",
            activity_start=c_nunez.activity_start,
            activity_end=2024,
            is_phd_in_progress=False,
            notes="Identidad corregida de Cristina Nuñez a Giovanni Nunes (PhD completado)."
        )
        session.add(g_nunes)
        session.flush()

        # Migrate relationships
        # As student
        rels_stu = session.query(Relationship).filter(Relationship.student_id == 'cristina_nunez').all()
        for rel in rels_stu:
            rel.student_id = 'giovanni_nunes'
            print(f"Migrated relationship (student): {rel.director_id} -> giovanni_nunes")
        
        # As director
        rels_dir = session.query(Relationship).filter(Relationship.director_id == 'cristina_nunez').all()
        for rel in rels_dir:
            rel.director_id = 'giovanni_nunes'
            print(f"Migrated relationship (director): giovanni_nunes -> {rel.student_id}")

        # Delete old record
        session.delete(c_nunez)
    else:
        # If he already exists, just update him
        g_nunes.name = "Giovanni Nunes"
        g_nunes.is_phd_in_progress = False
        g_nunes.role = "Investigador"
        session.delete(c_nunez) # Remove the fake Cristina

    session.commit()
    session.close()
    print("Fix complete: Giovanni Nunes is now the primary identity.")

if __name__ == "__main__":
    fix_giovanni()
