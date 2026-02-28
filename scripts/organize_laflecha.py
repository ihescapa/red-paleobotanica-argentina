import os
import shutil

SEARCH_DIR = "/Users/ignacioescapa"
DEST_DIR = "/Users/ignacioescapa/Desktop/La Flecha"
KEYWORDS = ["flecha"]
EXCLUDES = ["Library", "Applications", "System", "node_modules", "Adobe Photoshop", ".Trash", ".vscode", ".git", ".gemini"]
EXCLUDE_TERMS = ["flecha del tiempo", "time's arrow", "green arrow", "flecha verde"] # Common irrelevant matches

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
        
        # Check specific exclusion for path components
        if is_excluded(root):
            continue

        for filename in files:
            # Check matches
            match = False
            lower_name = filename.lower()
            
            # Check basic keywords
            for keyword in KEYWORDS:
                if keyword in lower_name:
                    match = True
                    break
            
            # exclude irrelevant terms
            if match:
                for term in EXCLUDE_TERMS:
                    if term in lower_name:
                        match = False
                        break
            
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
