
# Quiet Crawler Project Structure

This repository supports the Claude API-based incident analysis workflow. It includes scraper outputs, structured source data, codebook files, and utility scripts, all organized for clarity, auditability, and maintainability.

---

## 📂 Directory Structure

```
.
quiet-crawler/
│
├── sources/ # Final cleaned source text files, source numbering is independent from incident numbering
│   ├── ADM-001.txt
│   ├── DB-001.txt  # DB sources are a subset (by incident criteria) of raw outputs
│   ├── SOC-001.txt # Each SOC holds one reddit/IG/Twitter post 
│
├── _data/ # Manually curated markdown and YAML data files
│   ├── codebook.md
│   ├── codebook_w_coding_proto_v2.md
│   ├── source_master.yml
│   ├── field_definitions.yml
│
├── scraper_inputs/
│   ├── daily_bruin/
│   │   ├── universal_keywords.txt
│   │   └── universal_incident_rule.md
│   └── reddit/
│       ├── INC-001-reddit-urls.json
│       ├── INC-001-reddit-urls.json
│
├── scraper_outputs/ # Raw outputs from the web scraper 
│   ├── raw_text/
│   │   ├── DB-raw-001.txt
│   │   ├── INC-001_reddit-raw-001.txt # Flattened but still multiple posts in one file
│   ├── json/
│   │   ├── DB-raw-001.json
│   │   ├── INC-001_reddit_scaped.json # Dicts with metadata and comments
│
├── scrapers/ # Web scraping code modules
│   ├── init.py
│   ├── scraper_base.py
│   ├── reddit_scraper.py  
│   ├── daily_bruin_scraper.py
│
├── utils/ # Helper Python scripts
│   ├── source_reader.py
│   ├── json_to_txt_converter.py
│
├── api_tests/ # API test scripts for Claude integration
│   └── test_claude.py
│
├── outputs/ # Claude audit logs and YAML outputs per incident
│   ├── INC-001/
│   │   ├── audit-log.txt
│   │   └── coded-output.yml
│   ├── INC-002/
│   │   ├── audit-log.txt
│   │   └── coded-output.yml
│   └── ...
│
├── main.py # Entry point for running the full incident analysis pipeline
├── README.md # Project overview and directory structure
└── venv/ # Python virtual environment (created via python -m venv)

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
- Regularly update `field_definitions.yml` and `source_master.yml` to stay aligned with your evolving coding protocols.

---
