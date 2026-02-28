from models import Session, Researcher

def clean_database():
    db = Session()
    
    # 1. Fix 'Desconocido' Genders
    gender_updates = {
        'herbst_r': 'Masculino',
        'de_la_sota_er': 'Masculino',
        'pottie_de_baldis_d': 'Femenino', # Diana
        'elgorriaga_a': 'Masculino',
        'fernandez_pacella_l': 'Masculino',
        'fernandez_d': 'Masculino',
        'lafuente_diaz_m': 'Femenino',
        'perez_e': 'Femenino',
        'marisol_beltran': 'Femenino',
        'giovanni_nunes': 'Masculino',
        'passeggi_e': 'Masculino',
        'fernandez_da': 'Masculino',
        'beltran_m': 'Femenino',
        'carrizo_ma': 'Femenino',
        'elias_samalo_a': 'Masculino',
    }

    print("--- Updating Genders ---")
    for rid, gender in gender_updates.items():
        r = db.query(Researcher).get(rid)
        if r:
            r.gender = gender
            print(f"Updated {r.name} -> {gender}")
        else:
            print(f"Warning: Researcher {rid} not found.")

    # 2. Add / Expand Keywords for major figures
    kw_updates = {
        'herbst_r': 'Triásico, Helechos, Corystospermales',
        'de_la_sota_er': 'Helechos, Anatomía',
        'gandolfo_ma': 'Cretácico, Angiospermas, Patagonia',
        'wilf_p': 'Cenozoico, Angiospermas, Paleoclima, Patagonia',
        'johnson_k': 'Cretácico, Paleoceno, Angiospermas',
        'pittman_l': 'Coníferas, Patagonia',
        'beltran_m': 'Pérmico, Glosoptéridas, Paleobotánica',
        'carrizo_ma': 'Cretácico, Helechos, Anatomía',
        'elias_samalo_a': 'Cenozoico, Maderas, Paleobotánico',
        'moyano_m': 'Triásico, Cretácico, Palinología',
        'garcia_massini_j': 'Triásico, Permico, Fósiles, Interacciones Planta-Fungo',
        'escarapa_i': 'Jurásico, Coníferas, Triásico, Helechos, Cladística, Patagonia, Antártida, Paleobotánico, Filogenia',
        'passalia_mg': 'Cretácico, Angiospermas, Patagonia, Paleobotánico',
        'gonzalez_p': 'Cretácico, Patagonia, Paleobotánico',
        'krause_m': 'Cretácico, Paleógeno, Suelos, Paleobotánica',
        'bodnar_j': 'Triásico, Maderas, Anatomía, Paleobotánica',
        'vera_e': 'Jurásico, Helechos, Anatomía, Paleobotánica',
        'ameri_c': 'Triásico, Maderas',
        'brea_m': 'Cenozoico, Maderas, Anatomía, Paleobotánico, Cretácico'
    }

    print("\n--- Updating Keywords ---")
    count_kw = 0
    for rid, kws in kw_updates.items():
        r = db.query(Researcher).get(rid)
        if r:
            count_kw += 1
            existing = r.keywords if r.keywords else ""
            if existing:
                # Merge unique keywords
                existing_list = [k.strip().lower() for k in existing.split(',')]
                new_list = [k.strip() for k in kws.split(',')]
                for n in new_list:
                    if n.lower() not in existing_list:
                        existing += f", {n}"
                r.keywords = existing.strip(", ")
            else:
                r.keywords = kws
            print(f"Updated KWs for {r.name}: {r.keywords}")

    db.commit()
    db.close()
    print(f"\nFinished updating {len(gender_updates)} genders and {count_kw} keyword profiles.")

if __name__ == "__main__":
    clean_database()
