#!/usr/bin/env python3
"""
MPEB - Capture Success Page After Submit
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).parent)

async def capture_success_page():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: Playwright not installed")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] Capturing MPEB Success Page...")

    async with async_playwright() as p:
        browser = None
        try:
            # Launch visible browser
            print("Launching visible browser...")
            browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
            page = await browser.new_page()
            page.set_default_timeout(30000)

            # Navigate directly to form
            print("\nStep 1: Opening MPEB Application Form")
            print("URL: https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp\n")

            try:
                await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp", timeout=25000)
            except:
                print("(Page loading, continuing...)")

            await asyncio.sleep(3)

            # Find and fill IVRS field
            print("Step 2: Enter IVRS Number N3330008565")
            inputs = await page.query_selector_all("input[type='text']")
            print(f"Found {len(inputs)} text input fields\n")

            if inputs:
                for i, inp in enumerate(inputs):
                    placeholder = await inp.get_attribute("placeholder")
                    print(f"  Input {i}: {placeholder}")

                # Fill first input with IVRS
                await inputs[0].fill("N3330008565")
                print(f"\n✓ Filled IVRS number in first input field\n")
                await asyncio.sleep(1)

            # Wait for applicant name to populate
            print("Step 3: Waiting for Applicant Name to Auto-Populate")
            for wait_count in range(15):
                await asyncio.sleep(1)

                # Check all inputs for populated name
                all_inputs = await page.query_selector_all("input")
                for inp in all_inputs:
                    value = await inp.input_value()
                    if value and "AKSHAY" in value.upper() or "GARIMA" in value.upper():
                        print(f"✓ Applicant name found: {value}\n")
                        break

            # Take screenshot of form with applicant name populated
            print("Step 4: Capturing Screenshot of Form with Applicant Name Populated")
            screenshot_file = f"mpeb_success_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_file, full_page=True)
            print(f"✓ Screenshot saved: {screenshot_file}\n")

            # Find and click submit
            print("Step 5: Clicking Submit Button")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "submit" in text.lower():
                    print(f"Found: {text.strip()}")
                    await btn.click()
                    await asyncio.sleep(3)
                    print("✓ Submit clicked\n")
                    break

            # Capture post-submit page
            print("Step 6: Capturing Post-Submit Page")
            post_screenshot = f"mpeb_after_submit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=post_screenshot, full_page=True)
            print(f"✓ Post-submit screenshot: {post_screenshot}\n")

            # Log current URL
            print(f"Current URL: {page.url}\n")

            print("="*60)
            print("SUCCESS PAGE CAPTURED!")
            print("="*60)
            print("\nCheck these files:")
            print(f"  - {screenshot_file} (Form with applicant name)")
            print(f"  - {post_screenshot} (After submit)\n")

            print("Browser will close in 20 seconds...")
            await asyncio.sleep(20)

            return True

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            if browser:
                await asyncio.sleep(5)
            return False

        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass

if __name__ == "__main__":
    try:
        success = asyncio.run(capture_success_page())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
