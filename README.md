# MPEB Solar Application Automation

Automated Rooftop Solar Panel Application Tracker for MPEB (M.P. Pashchim Kshetra Vidyut Vitran Co. Ltd)

## Overview

This automation system:
- 🤖 Automatically submits MPEB solar panel applications every hour
- 📊 Generates an interactive dashboard with success/failure metrics
- 📝 Logs all automation runs with timestamps
- 📸 Captures screenshots of successful submissions
- 🔄 Auto-syncs all changes to GitHub

## Setup

### Prerequisites
- Python 3.8+
- Playwright browser automation library
- Windows Task Scheduler
- Git with GitHub account

### Installation

1. **Install Playwright:**
   ```bash
   pip install playwright
   python -m playwright install chromium
   ```

2. **Clone Repository:**
   ```bash
   git clone https://github.com/akshayptdr/mpeb-automation.git
   cd mpeb-automation
   ```

3. **Run Initial Test:**
   ```bash
   python mpeb_complete_automation.py
   ```

## How It Works

### 1. Automation Flow
The `mpeb_complete_automation.py` script:
1. Opens MPEB home page
2. Clicks "Rooftop Solar Applications" menu
3. Clicks "Roof Top Application" submenu
4. Accepts terms and conditions
5. Enters IVRS number in LT Connection User field
6. Submits the form
7. Verifies successful submission
8. Captures screenshot
9. Logs results to `mpeb_status.txt`
10. Regenerates dashboard
11. **Auto-pushes changes to GitHub**

### 2. Status Logging
Each run creates an entry in `mpeb_status.txt`:
```
[2026-04-24 08:32:58] SUCCESS: Form Submitted Successfully - Details Page Reached
[2026-04-24 08:39:55] SUCCESS: Form Submitted Successfully - Details Page Reached
```

### 3. Interactive Dashboard
Open `mpeb_dashboard.html` in your browser to view:
- Total runs, successes, failures
- Success rate percentage
- Hourly trend chart
- Recent activity log
- Last run status

## Automatic GitHub Sync

### How Auto-Push Works

**Method 1: Dashboard Generator (Recommended)**
- Every time the dashboard regenerates, it automatically:
  - Commits changes to `mpeb_status.txt` and `mpeb_dashboard.html`
  - Pushes to GitHub
  - Works even if you're not making manual commits

**Method 2: Git Hook (For Manual Commits)**
- Located in `.git/hooks/post-commit`
- Automatically pushes after every git commit
- Requires credentials to be configured

### Setup Credentials

**Option A: Use Git Credentials Helper (Recommended)**
```bash
git config --global credential.helper wincred
```
After this, enter your GitHub credentials once and they'll be cached.

**Option B: Use Personal Access Token (Secure)**
1. Create PAT at: https://github.com/settings/tokens
2. Use token as password when Git prompts

**Option C: SSH Key Setup**
```bash
ssh-keygen -t ed25519 -C "it@farmkart.com"
# Add public key to GitHub
git remote set-url origin git@github.com:akshayptdr/mpeb-automation.git
```

## Windows Task Scheduler Setup

### Create Hourly Task
1. Open Windows Task Scheduler
2. Create Basic Task:
   - **Name:** MPEB Solar Application Check
   - **Trigger:** Daily at 09:37 AM
   - **Advanced:** Repeat every 1 hour, indefinitely
   - **Action:** Start program
   - **Program:** `C:\Python312\python.exe`
   - **Arguments:** `C:\path\to\mpeb_complete_automation.py`

### Verify Task Status
```bash
tasklist | findstr python
Get-ScheduledTask -TaskName "MPEB Solar Application Check"
```

## File Structure

```
mpeb-automation/
├── mpeb_complete_automation.py       # Main automation script
├── mpeb_dashboard_generator.py       # Dashboard generator with auto-push
├── mpeb_status.txt                   # Status log (auto-generated)
├── mpeb_dashboard.html               # Interactive dashboard (auto-generated)
├── mpeb_success_applicant_*.png      # Screenshots (auto-generated)
└── .git/hooks/post-commit            # Git hook for auto-push
```

## Monitoring

### View Dashboard
```bash
# Open in browser
start mpeb_dashboard.html
```

### Check Latest Status
```bash
tail -10 mpeb_status.txt
```

### View Git History
```bash
git log --oneline -20
```

### Check GitHub Repository
Visit: https://github.com/akshayptdr/mpeb-automation

## Troubleshooting

### Auto-push not working?
1. Check credentials: `git config --list | grep credential`
2. Test push manually: `git push origin master`
3. Check internet connection
4. Verify GitHub credentials are valid

### Automation not running hourly?
1. Check Task Scheduler trigger settings
2. Verify "Repeat every: 1 hour, for duration of: Indefinitely"
3. Run manually to test: `python mpeb_complete_automation.py`

### Dashboard not updating?
1. Run generator manually: `python mpeb_dashboard_generator.py`
2. Check `mpeb_status.txt` for recent entries
3. Refresh browser (Ctrl+F5) to clear cache

## IVRS Number
Default IVRS Number: **N3330008565**
(Edit scripts if you need to change this)

## Support

For issues or questions:
1. Check `mpeb_status.txt` for error messages
2. Review the dashboard for trends
3. Check GitHub repository for latest updates
4. Run automation manually to diagnose issues

## License

This automation is for authorized testing and monitoring purposes only.

---

**Last Updated:** 2026-04-24
**Repository:** https://github.com/akshayptdr/mpeb-automation.git
