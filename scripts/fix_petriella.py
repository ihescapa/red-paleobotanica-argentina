from models import Session, Researcher, Relationship

session = Session()

# Ensure Bruno Petriella exists
petriella = session.query(Researcher).filter(Researcher.name.like('%Bruno Petriella%')).first()
if not petriella:
    petriella = Researcher(id='bruno_petriella', name='Bruno Petriella', role='Formador', institution='MLP')
    session.add(petriella)
    print("Created Bruno Petriella")

# Ensure Alba Zamuner exists
zamuner = session.query(Researcher).filter(Researcher.name.like('%Alba%Zamuner%')).first()
if not zamuner:
    # This is unlikely since Ari Iglesias is connected to her, but for safety
    zamuner = Researcher(id='alba_zamuner', name='Alba Berta Zamuner', role='Formador', institution='MLP')
    session.add(zamuner)
    print("Created Alba Zamuner")

# Ensure the relationship exists
if petriella and zamuner:
    rel = session.query(Relationship).filter_by(director_id=petriella.id, student_id=zamuner.id).first()
    if not rel:
        session.add(Relationship(director_id=petriella.id, student_id=zamuner.id, type='Primary'))
        print(f"Added relationship: {petriella.name} -> {zamuner.name}")
    else:
        print(f"Relationship already exists: {petriella.id} -> {zamuner.id}")

session.commit()
session.close()
