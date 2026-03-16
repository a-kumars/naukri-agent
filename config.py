"""
Configuration file for Naukri Agent
"""

# Job search keywords
JOB_KEYWORDS = [
    "Infrastructure Engineer",
    "Platform Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Site Reliability Engineer"
]

# Browser settings
HEADLESS_MODE = False  # Set to False for testing to see browser actions
BROWSER_TYPE = "chrome"  # Options: "chromium", "firefox", "webkit", "chrome", "edge"

# URLs
NAUKRI_BASE_URL = "https://www.naukri.com"
NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"

# Timeouts (in seconds)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 10

# Data file paths
JOBS_CSV_PATH = "data/jobs.csv"
LOG_FILE_PATH = "logs/agent.log"
RESUME_FILE_PATH = "naukri_agent/resume/Pragati Potadar_Resume (1).pdf"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"