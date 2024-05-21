import os

def get_file_by_path(path: str):
    with open(path, 'r') as f:
        key = f.read()
    return key
