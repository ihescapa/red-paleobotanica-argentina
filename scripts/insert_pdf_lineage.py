from models import Session, Researcher, Relationship
import sys

def insert_lineage():
    session = Session()
    
    # NEW RESEARCHERS (mostly Quaternary Palynologists)
    new_researchers = [
        {'id': 'prieto_a', 'name': 'Aldo R. Prieto', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC, UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'dantoni_h', 'name': 'Héctor L. D\'Antoni', 'role': 'Palinólogo', 'institution': 'UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'mancini_mv', 'name': 'María Virginia Mancini', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC, UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'paez_mm', 'name': 'Marta Mercedes Paez', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC, UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'borromei_am', 'name': 'Ana María Borromei', 'role': 'Palinólogo del Cuaternario', 'institution': 'INGEOSUR, UNS', 'notes': 'Source: Prieto2018'},
        {'id': 'grill_s', 'name': 'Silvia Grill', 'role': 'Palinólogo del Cuaternario', 'institution': 'INGEOSUR, UNS', 'notes': 'Source: Prieto2018'},
        {'id': 'lupo_lc', 'name': 'Liliana Concepción Lupo', 'role': 'Palinólogo del Cuaternario', 'institution': 'INECOA, UNJu', 'notes': 'Source: Prieto2018'},
        {'id': 'stutz_sm', 'name': 'Silvina María Stutz', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC, UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'burry_ls', 'name': 'L. Susana Burry', 'role': 'Palinólogo del Cuaternario', 'institution': 'UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'trivi_me', 'name': 'Matilde Elena Trivi', 'role': 'Palinólogo del Cuaternario', 'institution': 'UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'garralla_ss', 'name': 'Silvina Susana Garralla', 'role': 'Palinólogo del Cuaternario', 'institution': 'CECOAL', 'notes': 'Source: Prieto2018'},
        {'id': 'borel_cm', 'name': 'C. Marcela Borel', 'role': 'Palinólogo del Cuaternario', 'institution': 'INGEOSUR', 'notes': 'Source: Prieto2018'},
        {'id': 'vilanova_i', 'name': 'Isabel Vilanova', 'role': 'Palinólogo del Cuaternario', 'institution': 'MACN', 'notes': 'Source: Prieto2018'},
        {'id': 'tonello_ms', 'name': 'Marcela S. Tonello', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC', 'notes': 'Source: Prieto2018'},
        {'id': 'de_porras_me', 'name': 'María Eugenia de Porras', 'role': 'Palinólogo del Cuaternario', 'institution': 'IANIGLA', 'notes': 'Source: Prieto2018'},
        {'id': 'candel_ms', 'name': 'María Soledad Candel', 'role': 'Palinólogo del Cuaternario', 'institution': 'INGEOSUR', 'notes': 'Source: Prieto2018'},
        {'id': 'musotto_ll', 'name': 'Lorena Laura Musotto', 'role': 'Palinólogo del Cuaternario', 'institution': 'INGEOSUR', 'notes': 'Source: Prieto2018'},
        {'id': 'sottile_gd', 'name': 'Gonzalo David Sottile', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC', 'notes': 'Source: Prieto2018'},
        {'id': 'mourelle_d', 'name': 'Dominique Mourelle', 'role': 'Palinólogo del Cuaternario', 'institution': 'CURE, Uruguay', 'notes': 'Source: Prieto2018'},
        {'id': 'oxman_bi', 'name': 'Brenda Irene Oxman', 'role': 'Palinólogo del Cuaternario', 'institution': 'INECOA', 'notes': 'Source: Prieto2018'},
        {'id': 'velazquez_n', 'name': 'Nadia Velázquez', 'role': 'Palinólogo del Cuaternario', 'institution': 'UNMDP', 'notes': 'Source: Prieto2018'},
        {'id': 'echeverria_me', 'name': 'Marcos E. Echeverría', 'role': 'Palinólogo del Cuaternario', 'institution': 'IIMyC', 'notes': 'Source: Prieto2018'},
        # Historical / Senior
        {'id': 'caldenius_c', 'name': 'Carl Caldenius', 'role': 'Geólogo', 'institution': 'Suecia', 'notes': 'Source: Prieto2018'},
        {'id': 'von_post_ejl', 'name': 'Ernst Jakob Lennart von Post', 'role': 'Geólogo/Palinólogo', 'institution': 'Universidad de Estocolmo', 'notes': 'Source: Prieto2018'},
        {'id': 'auer_v', 'name': 'Väinö Auer', 'role': 'Geógrafo/Geólogo', 'institution': 'Finlandia', 'notes': 'Source: Prieto2018'},
        {'id': 'markgraf_v', 'name': 'Vera Markgraf', 'role': 'Palinólogo', 'institution': 'INSTAAR', 'notes': 'Source: Prieto2018'},
        {'id': 'heusser_cj', 'name': 'Calvin J. Heusser', 'role': 'Palinólogo', 'institution': 'EUA', 'notes': 'Source: Prieto2018'},
        {'id': 'rabassa_j', 'name': 'Jorge Rabassa', 'role': 'Geólogo', 'institution': 'CADIC', 'notes': 'Source: Prieto2018'},
        {'id': 'schabitz_f', 'name': 'Frank Schäbitz', 'role': 'Palinólogo', 'institution': 'Universidad de Colonia', 'notes': 'Source: Prieto2018'},
        {'id': 'garleff_k', 'name': 'Karsten Garleff', 'role': 'Geógrafo', 'institution': 'Alemania', 'notes': 'Source: Prieto2018'},
    ]
    
    for r_data in new_researchers:
        if not session.get(Researcher, r_data['id']):
            session.add(Researcher(**r_data))
        else:
            r = session.get(Researcher, r_data['id'])
            if r.notes and 'Source: Prieto2018' not in r.notes:
                r.notes += " / Source: Prieto2018"
            elif not r.notes:
                r.notes = "Source: Prieto2018"
    
    session.commit()
    
    relationships = [
        # D'Antoni Students
        ('dantoni_h', 'mancini_mv', 'Doctoral Director'),
        ('dantoni_h', 'prieto_a', 'Doctoral Director'),
        ('dantoni_h', 'paez_mm', 'Doctoral Director'),
        ('dantoni_h', 'bianchi_mm', 'Doctoral Director'),
        ('dantoni_h', 'burry_ls', 'Doctoral Director'),
        ('dantoni_h', 'trivi_me', 'Doctoral Director'),
        
        # Romero Students (Quaternary)
        # Assuming romero_ej is the ID for Edgardo Romero
        ('romero_ej', 'fernandez_ca', 'Doctoral Director'),
        ('romero_ej', 'trivi_me', 'Doctoral Director'),
        
        # Quattrocchio Students (Quaternary)
        ('quattrocchio_m', 'borromei_am', 'Doctoral Director'),
        ('quattrocchio_m', 'grill_s', 'Doctoral Director'),
        ('quattrocchio_m', 'garralla_ss', 'Doctoral Director'),
        ('quattrocchio_m', 'fernandez_al', 'Doctoral Director'),
        
        # Borromei Students
        ('borromei_am', 'ponce_jf', 'Doctoral Director'),
        ('borromei_am', 'candel_ms', 'Doctoral Director'),
        ('borromei_am', 'musotto_ll', 'Doctoral Director'),
        
        # Mancini Students
        ('mancini_mv', 'de_porras_me', 'Doctoral Director'),
        ('mancini_mv', 'marcos_ma', 'Doctoral Director'),
        ('mancini_mv', 'bamonte_fp', 'Doctoral Director'),
        ('mancini_mv', 'sottile_gd', 'Doctoral Director'),
        ('mancini_mv', 'echeverria_me', 'Doctoral Director'),
        
        # Prieto Students
        ('prieto_a', 'stutz_sm', 'Doctoral Director'),
        ('prieto_a', 'borel_cm', 'Doctoral Director'),
        ('prieto_a', 'vilanova_i', 'Doctoral Director'),
        ('prieto_a', 'tonello_ms', 'Doctoral Director'),
        ('prieto_a', 'de_porras_me', 'Doctoral Director'),
        ('prieto_a', 'mourelle_d', 'Doctoral Director'),
        
        # Lupo Students
        ('lupo_lc', 'oxman_bi', 'Doctoral Director'),
        ('lupo_lc', 'torres_gr', 'Doctoral Director'),
        
        # Others
        ('rabassa_j', 'borromei_am', 'Doctoral Director'),
        ('rabassa_j', 'ponce_jf', 'Doctoral Director'),
        ('garleff_k', 'schabitz_f', 'Doctoral Director'),
        ('garleff_k', 'lupo_lc', 'Doctoral Director'),
        ('heusser_cj', 'wingenroth_m', 'Doctoral Director'),
        ('markgraf_v', 'anderson_l', 'Doctoral Director'),
    ]
    
    # Check if 'bianchi_mm' exists (Bianchi, María M.)
    if not session.get(Researcher, 'bianchi_mm'):
        session.add(Researcher(id='bianchi_mm', name='María M. Bianchi', role='Palinólogo', institution='INALP', notes='Source: Prieto2018'))
        session.commit()

    for dir_id, stu_id, rel_type in relationships:
        # Check if relationship already exists
        exists = session.query(Relationship).filter_by(director_id=dir_id, student_id=stu_id).first()
        if not exists:
            # Check if both researchers exist
            dir_r = session.get(Researcher, dir_id)
            stu_r = session.get(Researcher, stu_id)
            if dir_r and stu_r:
                session.add(Relationship(director_id=dir_id, student_id=stu_id, type=rel_type))
            else:
                print(f"Warning: Missing researcher for {dir_id} -> {stu_id}")
                
    session.commit()
    session.close()
    print("PDF Lineage Extraction Batch 1 Complete (Refined)")

if __name__ == "__main__":
    insert_lineage()
