# Naukri Agent

A Python automation project that automates job search and profile updates on Naukri.com using Playwright for browser automation.

## Features

- Secure login using environment variables
- Automated resume upload and profile updates (twice daily)
- Job search using configurable keywords
- CSV storage with duplicate prevention
- Modular code structure ready for scheduling
- Comprehensive logging

## Installation

1. Clone or download the project:
   ```bash
   cd naukri_agent
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Naukri credentials:
   ```
   NAUKRI_EMAIL=your_email@example.com
   NAUKRI_PASSWORD=your_password
   ```

## Resume Setup

1. Place your resume file (PDF format) in the `resume/` directory
2. Update `RESUME_FILE_PATH` in `config.py` to match your resume filename
3. The agent will automatically upload this resume file during profile updates

## Setup Verification

After configuring your credentials, run the setup check:

```bash
python setup_check.py
```

This will verify that all components are properly configured before running the agent.

## Configuration

Edit `config.py` to customize:
- Job search keywords
- Browser settings (headless mode)
- Timeouts
- File paths (jobs CSV, resume file)

Place your resume file in the `resume/` directory and update `RESUME_FILE_PATH` in `config.py`.

## How to Run

### Manual Execution

Run the main script:
```bash
python main.py
```

Or run the scheduler function directly:
```bash
python scheduler.py
```

### Scheduling

The project is designed to be called by external schedulers. Use the `run_agent()` function from `scheduler.py`.

#### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task
3. Set trigger to run twice daily (7 AM and 7 PM)
4. Set action to start a program:
   - Program: `python.exe`
   - Arguments: `scheduler.py`
   - Start in: `path\to\naukri_agent`

#### Linux/Mac Cron

Add to crontab (`crontab -e`):

```bash
# Run at 7 AM and 7 PM daily
0 7,19 * * * cd /path/to/naukri_agent && python scheduler.py
```

## Project Structure

```
naukri_agent/
├─ main.py              # Main entry point
├─ setup_check.py       # Setup verification script
├─ config.py            # Configuration settings
├─ login.py             # Login functionality
├─ resume_updater.py    # Resume upload and profile update
├─ job_search.py        # Job search functionality
├─ storage.py           # CSV storage with deduplication
├─ scheduler.py         # Main agent runner
├─ utils/logger.py      # Logging utility
├─ resume/              # Directory for resume files
├─ .env                 # Environment variables (create from .env.example)
├─ .env.example         # Environment variables template
├─ requirements.txt     # Python dependencies
├─ README.md            # This file
└─ data/jobs.csv        # Job results storage
```

## Security Notes

- Credentials are loaded from environment variables only
- No hardcoded passwords in the code
- Use strong, unique passwords for Naukri account
- Consider using a dedicated Naukri account for automation

## Logging

Logs are saved to `logs/agent.log` with the following levels:
- INFO: General execution information
- WARNING: Non-critical issues
- ERROR: Critical errors

## Troubleshooting

1. **Login fails**: Check credentials in `.env` file
2. **Browser issues**: Ensure Playwright browsers are installed
3. **Permission errors**: Ensure write permissions for `data/` and `logs/` directories
4. **Network issues**: Check internet connection and Naukri.com availability

## Dependencies

- playwright: Browser automation
- python-dotenv: Environment variable management
- pandas: Data manipulation and CSV handling