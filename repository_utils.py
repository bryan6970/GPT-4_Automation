import os


def auto_import(missing_libraries, file):
    for library in missing_libraries:
        import_statement = f"{library}\n"
        with open(file, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(import_statement + content)
        print(f"Imported {library}")


def get_repo_dir():
    return os.path.dirname(os.path.abspath(__file__))
