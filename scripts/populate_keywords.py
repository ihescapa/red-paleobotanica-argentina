from models import Session, Researcher
import json

def populate_keywords():
    session = Session()
    
    # Keyword categories: Period, Organism/Field, Region, Methodology, Discipline
    profiles = {
        'escapa_i': ["Jurásico", "Coníferas", "Triásico", "Helechos", "Cladística", "Patagonia", "Antártida", "Paleobotánico", "Filogenia"],
        'sergio_archangelsky': ["Pérmico", "Triásico", "Cretácico", "Coníferas", "Bennettitales", "Patagonia", "Paleobotánico", "Cutículas"],
        'cuneo_r': ["Pérmico", "Triásico", "Jurásico", "Coníferas", "Ginkgoales", "Patagonia", "Paleobotánico", "Bioestratigrafía"],
        'barreda_v': ["Cenozoico", "Mioceno", "Palinólogo", "Angiospermas", "Patagonia", "Cuaternario", "Bioestratigrafía"],
        'artabe_a': ["Triásico", "Gondwana", "Corystospermales", "Paleobotánico", "Taxonomía", "Cutículas"],
        'zamuner_a': ["Triásico", "Jurásico", "Coníferas", "Araucariaceae", "Anatomía", "Paleobotánico"],
        'brea_m': ["Cenozoico", "Maderas", "Anatomía", "Paleobotánico", "Cretácico", "Cenozoico"],
        'ari_iglesias': ["Cretácico", "Paleogeno", "Angiospermas", "Patagonia", "Paleobotánico", "Paleoclima"],
        'prieto_a': ["Cuaternario", "Holoceno", "Palinólogo", "Ecología", "Arqueobotánica", "Pampa"],
        'dantoni_h': ["Cuaternario", "Palinólogo", "Ecología", "Modelado", "Estadística"],
        'quattrocchio_m': ["Cenozoico", "Jurásico", "Palinólogo", "Estratigrafía", "Cuaternario"],
        'romero_ej': ["Cretácico", "Cenozoico", "Angiospermas", "Paleobotánico", "Nothofagus"],
        'gamerro_jc': ["Cretácico", "Palinólogo", "Spora", "Taxonomía"],
        'petriella_b': ["Triásico", "Filogenia", "Paleobotánico", "Arquitectura foliar"],
        'gandolfo_ma': ["Cretácico", "Paleogeno", "Angiospermas", "Paleobotánico", "Filogenia"],
        'wilf_p': ["Cretácico", "Paleogeno", "Patagonia", "Angiospermas", "Paleoclima"],
        'johnson_k': ["Cretácico", "Paleogeno", "Extinción", "Angiospermas"],
        'pittman_l': ["Jurásico", "Coníferas", "Patagonia"],
        'krause_m': ["Cretácico", "Paleogeno", "Suelos", "Paleobotánico"],
        'passalia_mg': ["Cretácico", "Angiospermas", "Patagonia", "Paleobotánico"],
        'gonzalez_p': ["Cretácico", "Patagonia", "Paleobotánico"],
        'vera_e': ["Jurásico", "Helechos", "Anatomía", "Paleobotánico"],
        'bodnar_j': ["Triásico", "Maderas", "Anatomía", "Paleobotánico"],
        'beltran_m': ["Pérmico", "Glosoptéridas", "Paleobotánico"],
        'carrizo_ma': ["Cretácico", "Helechos", "Anatomía"],
        'elias_samalo_a': ["Cenozoico", "Maderas", "Paleobotánico"],
        'moyano_m': ["Triásico", "Cretácico", "Palinólogo"],
    }

    count = 0
    for rid, keywords in profiles.items():
        r = session.get(Researcher, rid)
        if r:
            # Join keywords into a comma-separated string
            r.keywords = ",".join(keywords)
            count += 1
            print(f"Updated keywords for {r.name} ({rid})")
        else:
            print(f"Researcher {rid} not found.")

    session.commit()
    session.close()
    print(f"Finished profiling {count} researchers.")

if __name__ == "__main__":
    populate_keywords()
