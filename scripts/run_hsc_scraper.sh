#!/bin/bash
# HSC Research Scraper - Monthly Update
# Schedule: 1st of each month at 8:00 AM
# Cron: 0 8 1 * * /Users/buuphan/Dev/Vietnam_dashboard/scripts/run_hsc_scraper.sh

set -e

# Configuration
PROJECT_DIR="/Users/buuphan/Dev/Vietnam_dashboard"
LOG_FILE="$PROJECT_DIR/logs/hsc_scraper.log"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Log start
echo "========================================" >> "$LOG_FILE"
echo "HSC Scraper Started: $(date)" >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Run scraper (credentials loaded from PROCESSORS/forecast/hsc/credentials.json)
$PYTHON PROCESSORS/forecast/hsc/run_hsc_scraper.py >> "$LOG_FILE" 2>&1

# Log completion
echo "HSC Scraper Completed: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Optional: Send notification (uncomment if needed)
# osascript -e 'display notification "HSC scraper completed" with title "Vietnam Dashboard"'
