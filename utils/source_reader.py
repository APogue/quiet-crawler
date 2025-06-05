import os
import yaml

# Constants
BASE_DIR = os.getcwd()
SOURCES_DIR = os.path.join(BASE_DIR, 'sources')
SOURCE_MASTER_PATH = os.path.join(BASE_DIR, '_data', 'source_master.yml')

def read_source_metadata():
    """Reads the source master YAML file for metadata."""
    with open(SOURCE_MASTER_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_sources_for_incident(incident_id):
    """
    Returns a list of source IDs associated with the given incident ID.
    """
    metadata_list = read_source_metadata()
    source_ids = [
        entry['id'] for entry in metadata_list
        if 'used_in' in entry and incident_id in entry['used_in']
    ]
    return source_ids

def load_source_content(source_id):
    """Loads a single source file by its ID (e.g., 'DB-001')."""
    txt_path = os.path.join(SOURCES_DIR, f"{source_id}.txt")
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Source file not found: {txt_path}")
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_source_with_metadata(source_id):
    """Gets both content and metadata for a specific source."""
    content = load_source_content(source_id)
    metadata_list = read_source_metadata()
    meta = next((item for item in metadata_list if item['id'] == source_id), None)
    return {
        'id': source_id,
        'content': content,
        'metadata': meta
    }

def prepare_sources_for_prompt(source_ids):
    """
    Assembles source texts (with inline IDs) for use in Claude prompts.
    Returns a single string with clear demarcation of source boundaries.
    """
    combined_text = ""
    for source_id in source_ids:
        try:
            content = load_source_content(source_id)
            combined_text += f"--- BEGIN SOURCE: {source_id} ---\n"
            combined_text += content.strip() + "\n"
            combined_text += f"--- END SOURCE: {source_id} ---\n\n"
        except FileNotFoundError as e:
            combined_text += f"--- MISSING SOURCE: {source_id} ---\n\n"
    return combined_text.strip()

def verify_source_ids_exist(source_ids):
    """
    Cross-checks that all provided source IDs exist in source_master.yml and on disk.
    Returns (missing_sources, missing_in_master).
    """
    metadata_list = read_source_metadata()
    master_ids = {item['id'] for item in metadata_list}
    missing_sources = []
    missing_in_master = []

    for source_id in source_ids:
        txt_path = os.path.join(SOURCES_DIR, f"{source_id}.txt")
        if not os.path.exists(txt_path):
            missing_sources.append(source_id)
        if source_id not in master_ids:
            missing_in_master.append(source_id)
    
    return missing_sources, missing_in_master



