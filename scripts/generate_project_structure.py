import os

# Folders and files to ignore completely
IGNORE_FOLDERS = {'.git', '__pycache__', '.pytest_cache', 'instance', 'venv'}
IGNORE_FILES = {'.DS_Store', 'zenday.db'}

def generate_structure(path, prefix=""):
    entries = sorted(os.listdir(path))
    structure = ""

    for index, entry in enumerate(entries):
        if entry in IGNORE_FOLDERS or entry.startswith(".") or entry in IGNORE_FILES:
            continue

        full_path = os.path.join(path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        structure += prefix + connector + entry + "\n"

        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if index == len(entries) - 1 else "│   ")
            structure += generate_structure(full_path, new_prefix)

    return structure

if __name__ == "__main__":
    project_root = "."  # Current directory
    structure_text = "Project Structure - Zenday Kroger Price Alert\n\n"
    structure_text += generate_structure(project_root)

    with open("PROJECT_STRUCTURE.txt", "w") as f:
        f.write(structure_text)

    print("✅ Project structure saved to PROJECT_STRUCTURE.txt")

