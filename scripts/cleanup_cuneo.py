import sqlite3

def run_cleanup():
    db_path = "/Users/ignacioescapa/Desktop/ANTIGRAVITY/genealogy.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Non-paleobotanists to remove
    to_remove = [
        "kevin_gomez",
        "ariana_robles",
        "agustin_perez",
        "carolina_oriozabala",
        "barbara_vallejo"
    ]

    print(f"Removing {len(to_remove)} non-paleobotanists...")
    for rid in to_remove:
        # Delete relationships where they are student or director
        cursor.execute("DELETE FROM relationships WHERE student_id = ? OR director_id = ?", (rid, rid))
        # Delete the researcher
        cursor.execute("DELETE FROM researchers WHERE id = ?", (rid,))
    
    # 2. Merge facundo_de_benedetti into de_benedetti_f
    print("Merging facundo_de_benedetti into de_benedetti_f...")
    # Update relationships: if facundo_de_benedetti was a student, now de_benedetti_f is the student
    cursor.execute("UPDATE relationships SET student_id = 'de_benedetti_f' WHERE student_id = 'facundo_de_benedetti'")
    # If facundo_de_benedetti was a director (unlikely but safe), update it
    cursor.execute("UPDATE relationships SET director_id = 'de_benedetti_f' WHERE director_id = 'facundo_de_benedetti'")
    # Remove the duplicate researcher entry
    cursor.execute("DELETE FROM researchers WHERE id = 'facundo_de_benedetti'")

    # 3. Link cristina_nunez to escapa_i
    print("Linking cristina_nunez to escapa_i...")
    # First remove any existing links for cristina_nunez that might be wrong (like to cuneo_r)
    cursor.execute("DELETE FROM relationships WHERE student_id = 'cristina_nunez' AND director_id IN ('cuneo_r', 'ruben_cuneo')")
    
    # Add link to escapa_i if not already there
    cursor.execute("SELECT 1 FROM relationships WHERE student_id = 'cristina_nunez' AND director_id = 'escapa_i'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO relationships (student_id, director_id, type) VALUES ('cristina_nunez', 'escapa_i', 'Doctorado')")

    conn.commit()
    conn.close()
    print("Cleanup complete.")

if __name__ == "__main__":
    run_cleanup()
