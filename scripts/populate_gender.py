from models import Session, Researcher

def populate_gender():
    session = Session()
    researchers = session.query(Researcher).all()
    count_m = 0
    count_f = 0
    count_u = 0
    
    # Common Spanish/Latin names prefix checking
    female_names = [
        "maría", "maria", "ana", "silvia", "viviana", "analía", "analia", "alba", "mariana", "mirta",
        "marta", "liliana", "silvina", "susana", "matilde", "marcela", "isabel", "eugenia", "soledad",
        "lorena", "dominique", "brenda", "nadia", "vera", "mercedes", "gabriela", "paula", "florencia",
        "claudia", "alejandra", "laura", "josefina", "carolina", "natalia", "daniela", "romina", "lucia",
        "lucía", "victoria", "agustina", "camila", "micaela", "valeria", "andrea", "patricia", "cristina",
        "beatriz", "norma", "graciela", "margarita", "carmen", "rosa", "teresa", "alicia", "ester"
    ]
    
    male_names = [
        "ignacio", "sergio", "rubén", "ruben", "ari", "aldo", "héctor", "hector", "juan", "carlos",
        "bruno", "ezequiel", "marcos", "gonzalo", "jorge", "edgardo", "alejandro", "eduardo", "roberto",
        "ricardo", "pedro", "pablo", "luis", "fernando", "diego", "martin", "martín", "nicolas", "nicolás",
        "facundo", "tomas", "tomás", "lucas", "matias", "matías", "santiago", "joaquin", "joaquín",
        "sebastián", "sebastian", "leandro", "maximiliano", "emanuel", "federico", "guillermo", "julio",
        "mario", "oscar", "daniel", "gustavo", "hugo", "victor", "víctor", "gabriel", "miguel", "angel",
        "angel", "horacio", "raul", "raúl", "arturo", "ernesto", "francisco", "carl", "ernst", "väinö",
        "calvin", "frank", "karsten", "wolfgang", "osvaldo", "armando", "carlos"
    ]
    
    manual_overrides = {
        'escapa_i': 'M',
        'cuneo_r': 'M',
        'zamuner_a': 'F',
        'ari_iglesias': 'M',
        'prieto_a': 'M',
        'dantoni_h': 'M',
        'bauer_v': 'M',
        'von_post_ejl': 'M',
        'caldenius_c': 'M',
        'auer_v': 'M',
        'grill_s': 'F',
        'lupo_lc': 'F',
        'burry_ls': 'F',
        'trivi_me': 'F',
        'garralla_ss': 'F',
        'borel_cm': 'F',
        'vilanova_i': 'F',
        'tonello_ms': 'F',
        'de_porras_me': 'F',
        'candel_ms': 'F',
        'musotto_ll': 'F',
        'sottile_gd': 'M',
        'mourelle_d': 'F',
        'oxman_bi': 'F',
        'velazquez_n': 'F',
        'echeverria_me': 'M',
        'markgraf_v': 'F',
        'heusser_cj': 'M',
        'rabassa_j': 'M',
        'schabitz_f': 'M',
        'garleff_k': 'M'
    }

    for r in researchers:
        first_name = r.name.split()[0].lower().replace(',', '')
        
        # Check overrides first
        if r.id in manual_overrides:
            r.gender = 'Femenino' if manual_overrides[r.id] == 'F' else 'Masculino'
        # Then check name lists
        elif first_name in female_names:
            r.gender = 'Femenino'
        elif first_name in male_names:
            r.gender = 'Masculino'
        # Heuristics for ambiguous names (e.g., ends in 'a' -> Female, 'o' -> Male)
        elif first_name.endswith('a'):
            r.gender = 'Femenino'
        elif first_name.endswith('o') or first_name.endswith('e'):
            r.gender = 'Masculino'
        else:
            r.gender = 'Desconocido'
            
        if r.gender == 'Masculino': count_m += 1
        elif r.gender == 'Femenino': count_f += 1
        else: count_u += 1

    session.commit()
    print(f"Gender Population Complete.\nMasculino: {count_m}\nFemenino: {count_f}\nDesconocido: {count_u}")
    
    # List unknowns for manual review if they consist of initials
    unknowns = session.query(Researcher).filter(Researcher.gender == 'Desconocido').all()
    if unknowns:
        print("\nReview needed for the following 'Desconocido' entries:")
        for u in unknowns:
            print(f"- {u.name} (ID: {u.id})")

    session.close()

if __name__ == "__main__":
    populate_gender()
