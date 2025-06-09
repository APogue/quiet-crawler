import os
import yaml

# Constants
BASE_DIR = os.getcwd()
SOURCES_DIR = os.path.join(BASE_DIR, 'sources')
INCIDENT_DATA_PATH = os.path.join(BASE_DIR, '_data', 'incident_data.yml')

def read_incident_data():
    """Reads the incident data YAML file."""
    with open(INCIDENT_DATA_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_incident_info(incident_id):
    """
    Returns incident info including sources list for the given incident ID.
    Returns dict with keys: id, date, summary, scope, sources
    """
    incident_list = read_incident_data()
    incident_info = next((item for item in incident_list if item['id'] == incident_id), None)
    if not incident_info:
        raise ValueError(f"Incident {incident_id} not found in incident_data.yml")
    return incident_info

def get_sources_for_incident(incident_id):
    """
    Returns a list of source IDs associated with the given incident ID.
    Validates that all source files exist before returning.
    Raises FileNotFoundError if any sources are missing.
    """
    incident_info = get_incident_info(incident_id)
    source_ids = incident_info.get('sources', [])
    
    # Check that all source files exist
    missing_sources = []
    for source_id in source_ids:
        txt_path = os.path.join(SOURCES_DIR, f"{source_id}.txt")
        if not os.path.exists(txt_path):
            missing_sources.append(source_id)
    
    if missing_sources:
        raise FileNotFoundError(f"Missing source files for incident {incident_id}: {missing_sources}")
    
    return source_ids

def load_source_content(source_id):
    """Loads a single source file by its ID (e.g., 'DB-001')."""
    txt_path = os.path.join(SOURCES_DIR, f"{source_id}.txt")
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"Source file not found: {txt_path}")
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def prepare_documents_for_api(source_ids):
    """
    Prepares source documents for the new Claude API document format.
    Returns a list of document objects ready for the API.
    """
    documents = []
    
    for source_id in source_ids:
        content = load_source_content(source_id)
        documents.append({
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": content
            },
            "title": source_id,  # This will help with citations
            "citations": {"enabled": True}
        })
    
    return documents