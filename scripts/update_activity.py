from models import Session, Researcher

updates = {
    "archangelsky_s": (1966, 2014),
    "volkheimer_w": (1968, 2015),
    "herbst_r": (1963, 2017),
    "cuneo_r": (1988, 2024),
    "quattrocchio_m": (1975, 2024),
    "artabe_a": (1984, 2020),
    "azcuy_cl": (1969, 2023), # Published posthumously or long career
    "gnaedinger_s": (1999, 2023),
    "pramparo_m": (2007, 2024),
    "ottone_e": (1999, 2026),
    "stipanicic_p": (1946, 2008), 
    "menendez_c": (1948, 1976),
    "brea_m": (1993, 2025),
    "bodnar_j": (2010, 2024), # Estimate based on thesis 2010
    "gutierrez_p": (1988, 2024), # Estimate based on thesis 1988
    "di_pasquo_m": (1999, 2024)  # Estimate based on thesis 1999
}

session = Session()

for r_id, (start, end) in updates.items():
    r = session.query(Researcher).filter_by(id=r_id).first()
    if r:
        r.activity_start = start
        r.activity_end = end
        print(f"Updated {r.name}: {start}-{end}")
    else:
        print(f"Researcher {r_id} not found.")

session.commit()
session.close()
