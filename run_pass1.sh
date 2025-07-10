#!/bin/bash

# run_pass1.sh – hardcoded test runner for Pass 1 condensation

# Usage:

# chmod +x run_pass1.sh    # (only once to make the scrip executable)

# ./run_pass1.sh

# When ready to remove the dry-run and actually call Claude, edit that last line: --dry-run

python -m pipeline.run_pass1_condense_policy \
  --incident-id INC-001 \
  --source-id PHIL-001 \
  #--dry-run
