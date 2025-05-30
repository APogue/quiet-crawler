# utils/source_reader.py
import os
import yaml

SOURCES_DIR = os.path.join(os.getcwd(), 'sources')
SOURCE_MASTER_PATH = os.path.join(os.getcwd(), '_data', 'source_master.yml')

def read_source_files():
    """Reads all .txt files in the sources/ directory."""
    sources = {}
    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith('.txt'):
            file_id = filename.replace('.txt', '')
            file_path = os.path.join(SOURCES_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                sources[file_id] = f.read()
    return sources

def read_source_metadata():
    """Reads the source master YAML file for metadata."""
    with open(SOURCE_MASTER_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_source_with_metadata(source_id):
    """Gets both content and metadata for a specific source."""
    sources = read_source_files()
    metadata = read_source_metadata()
    
    content = sources.get(source_id)
    meta = next((item for item in metadata if item['id'] == source_id), None)
    
    return {
        'id': source_id,
        'content': content,
        'metadata': meta
    }
