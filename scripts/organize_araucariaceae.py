import os
import shutil
import fnmatch

SEARCH_DIR = "/Users/ignacioescapa"
DEST_DIR = "/Users/ignacioescapa/Desktop/Araucariaceae_Recopilacion"
KEYWORDS = ["*araucariaceae*", "*matrix*", "*matriz*"]
EXCLUDES = ["Library", "Applications", "System", "node_modules", "Adobe Photoshop", ".Trash", ".vscode", ".git", ".gemini"]

def is_excluded(path):
    parts = path.split(os.sep)
    for part in parts:
        if part in EXCLUDES or part.startswith('.'):
            return True
    return False

def get_unique_path(dest_dir, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    dest_path = os.path.join(dest_dir, new_filename)
    while os.path.exists(dest_path):
        new_filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(dest_dir, new_filename)
        counter += 1
    return dest_path

def main():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    count = 0
    print(f"Starting search in {SEARCH_DIR}...")
    
    for root, dirs, files in os.walk(SEARCH_DIR):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDES and not d.startswith('.')]
        
        # Check specific exclusion for path components (double check)
        if is_excluded(root):
            continue

        for filename in files:
            # Check matches
            match = False
            lower_name = filename.lower()
            if "araucariaceae" in lower_name:
                match = True
            elif "matrix" in lower_name or "matriz" in lower_name:
                # Refine matrix search to avoid system files or excessively generic ones
                # But user asked for "matrices filogeneticas" or "lo que sea".
                # Common extensions for matrices: .tnt, .nex, .phy, .txt, .doc, .xls
                # If it's just "matrix.js" it's likely code.
                if lower_name.endswith(('.js', '.h', '.c', '.cpp', '.py', '.html', '.css', '.json', '.xml', '.inl')):
                     match = False
                else:
                    match = True
            
            if match:
                src_path = os.path.join(root, filename)
                dest_path = get_unique_path(DEST_DIR, filename)
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied: {src_path} -> {dest_path}")
                    count += 1
                except Exception as e:
                    print(f"Error copying {src_path}: {e}")

    print(f"Finished. Total files copied: {count}")

if __name__ == "__main__":
    main()
