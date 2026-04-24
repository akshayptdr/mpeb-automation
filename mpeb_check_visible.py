#!/usr/bin/env python3
"""
MPEB Check Script - Visible Browser Version
Run this to see what's happening on the page
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).parent)

async def check_mpeb_application():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: Playwright not installed")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Starting MPEB check (VISIBLE BROWSER)...")
    print("Keep this browser window open to see what's happening")

    async with async_playwright() as p:
        try:
            # Launch with visible browser
            browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
            page = await browser.new_page()
            page.set_default_timeout(10000)

            print("\n1. Opening website...")
            await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/rtpfront", timeout=15000)
            await asyncio.sleep(3)

            print("2. Looking for 'Agree and Continue' button to click...")
            # Try to find the button
            try:
                button = await page.wait_for_selector("button, input[type='button'], input[value*='Agree']", timeout=5000)
                print("   Found button, clicking...")
                await button.click()
                await asyncio.sleep(2)
            except:
                print("   Button not found, scrolling down...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            print("3. Checking current URL...")
            current_url = page.url
            print(f"   Current URL: {current_url}")

            print("4. Enter IVRS number N3330008565...")
            input(f"   >> MANUAL: Enter the IVRS number when ready, then press ENTER here: ")

            print("5. Click Submit button...")
            input(f"   >> MANUAL: Click the Submit button on the page, then press ENTER here: ")

            print("6. Checking if form was submitted...")
            await asyncio.sleep(2)
            current_url = page.url
            print(f"   Current URL: {current_url}")

            print("\nTest completed. Browser will close in 10 seconds...")
            await asyncio.sleep(10)
            await browser.close()
            return True

        except Exception as e:
            print(f"ERROR: {str(e)}")
            print("\nBrowser will close in 5 seconds...")
            await asyncio.sleep(5)
            try:
                await browser.close()
            except:
                pass
            return False

if __name__ == "__main__":
    try:
        success = asyncio.run(check_mpeb_application())
        print(f"\nDone. Exit code: {0 if success else 1}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
