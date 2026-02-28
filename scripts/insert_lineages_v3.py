from models import Session, Researcher, Relationship
from datetime import datetime

def insert_data():
    session = Session()
    
    # helper to get or create researcher
    def get_or_create_researcher(id, name, role="Investigador", inst=None):
        r = session.query(Researcher).filter_by(id=id).first()
        if not r:
            r = Researcher(id=id, name=name, role=role, institution=inst)
            session.add(r)
            print(f"Created researcher: {name}")
        return r

    # helper to add relationship
    def add_rel(dir_id, stu_id, type="Primary"):
        rel = session.query(Relationship).filter_by(director_id=dir_id, student_id=stu_id).first()
        if not rel:
            session.add(Relationship(director_id=dir_id, student_id=stu_id, type=type))
            print(f"Added relationship: {dir_id} -> {stu_id}")

    # --- ARI IGLESIAS SCHOOL ---
    # Ari's director: Alba Berta Zamuner
    zamuner = get_or_create_researcher("alba_zamuner", "Alba Berta Zamuner", "Formador", "MLP")
    ari = get_or_create_researcher("ari_iglesias", "Ari Iglesias", "Investigador", "INIBIOMA")
    add_rel("alba_zamuner", "ari_iglesias")

    # Ari's students
    m_beltran = get_or_create_researcher("marisol_beltran", "Marisol Beltrán", "Becario", "INIBIOMA")
    e_silva = get_or_create_researcher("eva_silva_bandeira", "Eva María Silva Bandeira", "Becario", "INIBIOMA")
    add_rel("ari_iglesias", "marisol_beltran")
    add_rel("ari_iglesias", "eva_silva_bandeira")

    # --- RUBEN CUNEO SCHOOL ---
    # Ruben's director: Sergio Archangelsky
    sergio = get_or_create_researcher("sergio_archangelsky", "Sergio Archangelsky", "Pionero", "MLP / MACN")
    cuneo = get_or_create_researcher("ruben_cuneo", "Ruben Cúneo", "Formador", "MEF")
    add_rel("sergio_archangelsky", "ruben_cuneo")

    # Ruben's students
    students = [
        ("andres_elgorriaga", "Andrés Elgorriaga"),
        ("ana_andruchow", "Ana Andruchow Colombo"),
        ("kevin_gomez", "Kevin Gómez"),
        ("ariana_robles", "Ariana Robles Vilches"),
        ("facundo_de_benedetti", "Facundo De Benedetti"),
        ("agustin_perez", "Agustín Pérez Moreno"),
        ("carolina_oriozabala", "Carolina Oriozabala"),
        ("cristina_nunez", "Cristina Nuñez"),
        ("barbara_vallejo", "Bárbara Vallejo")
    ]

    for s_id, s_name in students:
        get_or_create_researcher(s_id, s_name, "Becario", "MEF")
        add_rel("ruben_cuneo", s_id)

    session.commit()
    session.close()
    print("Insertion complete.")

if __name__ == "__main__":
    insert_data()
