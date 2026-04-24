#!/usr/bin/env python3
"""
MPEB Check Script - Manual Browser Version
Opens the URL in your default browser, you do the steps manually
"""
import webbrowser
import time
from datetime import datetime
from pathlib import Path

log_file = Path("mpeb_check_log.txt")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"[{timestamp}] MPEB Application Check")
print("=" * 50)
print("\nOpening MPEB website in your browser...")

# Open the website in default browser
webbrowser.open("https://mpwzservices.mpwin.co.in/mpeb_english/rtpfront")

print("\nPlease do the following steps in the browser that just opened:")
print("\n1. Accept the terms and conditions")
print("2. Enter IVRS Number: N3330008565")
print("3. Click Submit button")
print("4. Wait for the applicant name to appear")
print("\nAfter you complete these steps, come back and press ENTER here...")

# Wait for user to complete steps
input("\nPress ENTER when done: ")

# Log the check
log_message = f"[{timestamp}] Manual check completed\n"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(log_message)

print(f"\nCheck logged to {log_file}")
print("All done!")
