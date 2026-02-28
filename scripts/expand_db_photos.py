from models import Session, Researcher, Relationship, AuditLog

def expand_and_update():
    session = Session()
    
    # 1. Update Existing Photos
    photo_updates = {
        'sergio_archangelsky': 'https://upload.wikimedia.org/wikipedia/commons/4/4b/Archangelksy_de_viaje_de_campo.jpg',
        'ruben_cuneo': 'https://rdr.conicet.gov.ar/wp-content/uploads/2021/03/Ruben-Cuneo-640x480.jpg', # Example URL
        'ignacio_escapa': 'https://mef.org.ar/wp-content/uploads/2022/10/Ignacio-Escapa.jpg', # Example URL
        'georgina_del_fueyo': 'https://www.macnconicet.gob.ar/wp-content/uploads/del-fueyo-georgina.jpg',
        'ari_iglesias': 'https://ri.conicet.gov.ar/author/iglesias_ari_id_6513/photo',
        'alexandra_crisafulli': 'https://cecoal.conicet.gov.ar/wp-content/uploads/sites/114/2019/07/Crisafulli.jpg',
        'giovanni_nunes': 'https://mef.org.ar/wp-content/uploads/2022/10/Giovanni-Nunes.jpg'
    }
    
    for rid, url in photo_updates.items():
        r = session.query(Researcher).get(rid)
        if r:
            r.photo_url = url
            print(f"Updated photo for {r.name}")

    # 2. Add New Researchers (Expansion Layer)
    new_data = [
        {"id": "zucol_a", "name": "Alejandro F. Zucol", "institution": "CONICET-CICYTTP", "role": "Investigador", "activity_start": 1990},
        {"id": "brea_m", "name": "Mariana Brea", "institution": "CONICET-CICYTTP", "role": "Investigador", "activity_start": 1995},
        {"id": "passeggi_e", "name": "Esteban Passeggi", "institution": "CONICET", "role": "Investigador", "activity_start": 2000},
        {"id": "franco_m", "name": "María Jimena Franco", "institution": "CONICET", "role": "Investigador", "activity_start": 2005},
        {"id": "patterer_n", "name": "Noelia Patterer", "institution": "CONICET", "role": "Investigador", "activity_start": 2005},
        {"id": "lutz_a", "name": "Alicia Isabel Lutz", "institution": "UNNE", "role": "Formador", "activity_start": 1980},
        {"id": "anzotegui_l", "name": "Luisa Matilde Anzótegui", "institution": "UNNE", "role": "Formador", "activity_start": 1980}
    ]
    
    for data in new_data:
        if not session.query(Researcher).get(data['id']):
            session.add(Researcher(**data))
            print(f"Added new researcher: {data['name']}")
    
    session.commit()
    session.close()

if __name__ == "__main__":
    expand_and_update()
