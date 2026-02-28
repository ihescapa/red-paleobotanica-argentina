import sqlite3

def run_deep_cleanup():
    db_path = "/Users/ignacioescapa/Desktop/ANTIGRAVITY/genealogy.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Mapping of Inconsistent IDs (Source -> Destination)
    normalize_map = {
        "ruben_cuneo": "cuneo_r",
        "andres_elgorriaga": "elgorriaga_a",
        "ana_andruchow": "andruchow_a",
        "andruchow_c": "andruchow_a",
        "facundo_de_benedetti": "de_benedetti_f",
        "nadia_woloszyn": "woloszyn_n",
        "giovanni_nunes": "nunes_g",
        "nunes_c": "nunes_g"
    }

    for src, dst in normalize_map.items():
        if src == dst: continue
        print(f"Normalizing {src} -> {dst}...")
        
        # 1. Update relationships where src is student
        cursor.execute("UPDATE relationships SET student_id = ? WHERE student_id = ?", (dst, src))
        
        # 2. Update relationships where src is director
        cursor.execute("UPDATE relationships SET director_id = ? WHERE director_id = ?", (dst, src))
        
        # 3. If dst doesn't exist in researchers, rename src to dst. 
        # Otherwise, delete src and keep dst.
        cursor.execute("SELECT 1 FROM researchers WHERE id = ?", (dst,))
        if cursor.fetchone():
            # dst exists, delete src researcher
            cursor.execute("DELETE FROM researchers WHERE id = ?", (src,))
        else:
            # dst doesn't exist, rename src researcher
            cursor.execute("UPDATE researchers SET id = ? WHERE id = ?", (dst, src))

    # 4. Remove exact duplicate relationships (same student, same director)
    print("Removing duplicate relationships...")
    cursor.execute("""
        DELETE FROM relationships 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM relationships 
            GROUP BY student_id, director_id
        )
    """)

    conn.commit()
    conn.close()
    print("Deep normalization complete.")

if __name__ == "__main__":
    run_deep_cleanup()
