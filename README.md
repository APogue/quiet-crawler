
# Quiet Crawler Project Structure

This repository supports the Claude API-based incident analysis workflow. It includes scraper outputs, structured source data, codebook files, and utility scripts, all organized for clarity, auditability, and maintainability.

---

## 📂 Directory Structure

```
.
quiet-crawler/
├── main.py                           # Master runner: executes both Pass 1 and Pass 2
├── run_pass1.sh                      # Test script
├── pipeline/                         # Modular task scripts
│   ├── run_pass1_condense_policy.py   # Standalone: condense PHIL-/POL- policy source files
│   └── run_pass2_code_incident.py     # Standalone: run full incident coding via Claude
├── claude_interface/                   # Claude interface layer
│   ├── __init__.py
│   └── claude_api.py                       # One-shot Claude runner (used by all other scripts, raw HTTP or SDK call)
├── sources/                            # Final cleaned source text files (used for incident coding)
│   ├── ADM-001.txt
│   ├── DB-001.txt                       # DB sources are a chosen subset (by incident criteria) of scraped articles
│   ├── SOC-001.txt                      # Each SOC is one reddit/IG/Twitter post (images are post-processed to txt)
│   └── images/
│       └── SOC-001.png                  # Pre-processed image source files
├── _data/                            # Structured metadata and configuration
│   ├── incident_data.yml             # Central list of all incident records
│   ├── source_master.yml             # Maps source IDs to files and descriptions
│   └── variable_data.yml             # YAML schema of all variable fields
├── inputs/                            # Claude API prompt inputs (modular, editable)
│   ├── system/                             # System-level configuration (shared across all incidents)
│   │   ├── system_role.txt                   # Claude's persona (e.g., "You are an evidence auditor...")
│   │   ├── justification_protocol.txt        # How to extract and attribute quotes and output justification block (YAML format)
│   │   ├── definitions.txt                   # Incident boundaries, source types, codebook meta-rules
│   │   ├── codebook.md                       # Variable dictionary with descriptions and values
│   │   ├── codebook_protocol.md              # Logic for applying codebook (e.g., disqualifying evidence checks)
│   │   ├── verifications.txt                 # Claude must confirm checklist (e.g. "I have reviewed all sources")
│   │   ├── codebook.md                       # Public-facing variable definitions
│   │   └── codebook_w_coding_proto_v2.md     # Codebook with integrated Claude-specific logic
│   └── incident/                           # Per-incident user message inputs
│       └── coding_workflow.txt               # Central command points to modules, then requests COT, verification and justification
├── outputs/                          # All Claude-generated outputs
│   ├── audit_log/                    # Full Claude input/output logs (pass 1 + pass 2)
│   │   └── INC-001/     
│   │       ├── INC-001-policy-POL-003-input.json
│   │       ├── INC-001-policy-POL-003-response.txt
│   │       ├── INC-001-input.json
│   │       └── INC-001-response.txt
│   ├── condensation/                 # Claude-processed policy summaries
│   │   └── INC-001/
│   │       └── INC-001-policy-POL-003-condensed.txt
│   ├── coded_raw/                     # Claude YAML + justifications (before validation)
│   │   └── INC-001-justified-output.yml
│   └── coded_values/                  # Final parsed and validated YAML output (values only)
│       └── INC-001-output.yml  
├── utils/                            # Shared utilities
│   ├── __init__.py
│   ├── doc_loader.py                 # Load incident metadata, sources, and system files
│   ├── preprocess_payload.py         # Construct Claude input payloads (messages + docs)
│   ├── path_manager.py               # generate file paths 
│   ├── logger.py                     # Save inputs and outputs for traceability
│   ├── test_claude.py                # Handles Claude interaction during testing phase
│   ├── reddit_json_to_txt_converter.py   # Flattens scraped Reddit data into clean .txt
│   └── txt_to_yaml_converter.py          # Converts Claude text output to structured YAML
├── scrapers/                           # Web scraping logic
│   ├── __init__.py
│   ├── reddit_scraper.py
│   └── daily_bruin_scraper.py
├── scraper_inputs/                     # Scraping input config
│   ├── daily_bruin/
│   │   ├── universal_keywords.yml
│   │   └── universal_incident_rule.md
│   └── reddit/
│       └── INC-001-reddit-urls.json
├── scraper_outputs/                    # Raw scraped data before cleaning
│   ├── raw_text/
│   │   ├── DB-raw-001.txt              # All scraped DB articles
│   │   └── INC-001_reddit-scraped.txt  # Flattened, multiple posts in one file
│   └── json/
│       ├── DB-raw-001.json             
│       └── INC-001_reddit_scraped.json # Dicts with metadata and comments
├── README.md                           # Project overview + file usage
└── venv/                               # Python virtual environment
```
---

## Key Folder Notes

- **sources/** — Contains the finalized .txt files that Claude will cite. Each file matches a source ID defined in `source_master.yml`.
- **_data/** — Contains structured metadata:
  - `source_master.yml` — Maps source IDs (e.g. ADM-001) to filenames and descriptions.
  - `field_definitions.yml` — Defines variables, types, and valid values for consistency and validation.
- **scraper_outputs/** — Raw outputs from the web scraper:
  - `raw_text/` — Unprocessed text dumps for debugging and reprocessing.
  - `json/` — Structured JSON outputs from scrapers, useful for transforming into .txt files.
- **scrapers/** — Dedicated Python modules for web scraping tasks:
  - Keeps scraper code organized by source (e.g. Daily Bruin, social media).
  - Allows easy maintenance and extension of scraping logic.
- **utils/** — Python scripts that support reading sources, metadata, and transforming scraper outputs:
  - `source_reader.py` — Loads text sources and metadata into memory.
  - `json_to_txt_converter.py` — Converts JSON outputs into clean .txt files that Claude can process.
- **api_tests/** — Contains test scripts to verify Claude API integration with sample prompts and documents.
- **main.py** — The main script that orchestrates the full pipeline, including processing incidents in batch and coordinating Claude API calls.
- **venv/** — Your isolated Python environment to install dependencies without polluting the system environment.

---

## Scraping criteria

### Reddit

It is a 10-5-5 model now, update. 

```
.
📄 Post (submission)
  ├── 💬 Top-Level Comment 1
  │     ├── ↪️ Reply 1.1
  │     │     ├── ↪️ Reply 1.1.1
  │     │     └── ↪️ Reply 1.1.2
  │     ├── ↪️ Reply 1.2
  │     │     ├── ↪️ Reply 1.2.1
  │     │     └── ↪️ Reply 1.2.2
  │     ├── ↪️ Reply 1.3
  │     │     ├── ↪️ Reply 1.3.1
  │     │     └── ↪️ Reply 1.3.2
  │     └── ↪️ Reply 1.4
  │           ├── ↪️ Reply 1.4.1
  │           └── ↪️ Reply 1.4.2
  │
  ├── 💬 Top-Level Comment 2
  │     ├── ↪️ Reply 2.1
  │     │     ├── ↪️ Reply 2.1.1
  │     │     └── ↪️ Reply 2.1.2
  │     └── ... (repeats similar structure as above)
  │
  └── 💬 Top-Level Comment 3-10
        └── ... (same nested structure as above)

```  
---

## Workflow

1. **Scrape Data** — Use the scrapers in `scrapers/` to collect raw data.
2. **Convert Outputs** — Transform JSON or raw text into cleaned `.txt` files in `sources/`.
3. **Organize Metadata** — Maintain `source_master.yml` and `field_definitions.yml` in `_data/`.
4. **Run Tests** — Use `api_tests/test_claude.py` to test Claude prompts and validate output structure.
5. **Full Pipeline** — Execute `main.py` to process incidents in batch, enforce coding protocols, and generate structured YAML outputs.

---

## Tips

- Keep `sources/` clean and consistent—one file per source ID, always matching `source_master.yml`.
- Keep `scraper_outputs/` intact as your raw record—don’t edit files there directly.
- Regularly update `variable_data.yml` and `source_master.yml` to stay aligned with your evolving coding protocols.

---
