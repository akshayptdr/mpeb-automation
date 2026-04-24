#!/usr/bin/env python3
"""
MPEB - Direct Form Access and Screenshot Capture
Go directly to form URL and capture applicant name population
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).parent)

async def capture_applicant_name():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: Playwright not installed")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] MPEB Application Verification\n")

    async with async_playwright() as p:
        browser = None
        try:
            # Launch visible browser
            print("Launching browser with visible window...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--no-sandbox"]
            )
            page = await browser.new_page()
            page.set_default_timeout(20000)

            # Step 1: Navigate directly to form
            print("\n=== STEP 1: Opening MPEB Application Form ===")
            print("URL: https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp\n")

            try:
                await page.goto(
                    "https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp",
                    timeout=20000
                )
                print("✓ Form page loaded\n")
            except:
                print("(Page loading took longer, continuing...)\n")

            await asyncio.sleep(3)

            # Step 2: Find and fill IVRS field
            print("=== STEP 2: Entering IVRS Number ===\n")

            inputs = await page.query_selector_all("input[type='text']")
            print(f"Found {len(inputs)} text input fields")

            if inputs:
                for i, inp in enumerate(inputs):
                    placeholder = await inp.get_attribute("placeholder")
                    print(f"  Input {i}: {placeholder}")

                # Fill IVRS in first input
                print(f"\nFilling IVRS number in first input field...")
                await inputs[0].fill("N3330008565")
                await asyncio.sleep(2)
                print("✓ IVRS N3330008565 entered\n")

            # Step 3: Wait for applicant name to auto-populate
            print("=== STEP 3: Waiting for Applicant Name to Auto-Populate ===\n")

            applicant_name = None
            name_input = None

            # Find name field
            name_inputs = await page.query_selector_all(
                "input[placeholder*='Name'], input[placeholder*='Applicant']"
            )

            if name_inputs:
                print(f"Found {len(name_inputs)} potential name field(s)\n")

                # Wait for population
                for attempt in range(20):
                    name_value = await name_inputs[0].input_value()
                    print(f"  Attempt {attempt + 1}: '{name_value}'")

                    if name_value and len(name_value.strip()) > 3:
                        applicant_name = name_value
                        name_input = name_inputs[0]
                        print(f"\n✓✓✓ APPLICANT NAME POPULATED: {applicant_name} ✓✓✓\n")
                        break

                    await asyncio.sleep(1)

            # Step 4: Capture screenshot of form with populated applicant name
            print("=== STEP 4: Capturing Screenshot ===\n")

            screenshot_file = f"mpeb_APPLICANT_NAME_FORM_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            print(f"Capturing: {screenshot_file}")
            await page.screenshot(path=screenshot_file, full_page=False)
            print(f"✓ Screenshot saved!\n")

            # Log success
            if applicant_name:
                log_file = Path("mpeb_check_log.txt")
                log_entry = f"[{timestamp}] SUCCESS: Applicant Name = {applicant_name}\n"
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                print(f"✓ Results logged to mpeb_check_log.txt\n")

            print("="*70)
            print("SCREENSHOT CAPTURED WITH APPLICANT NAME POPULATED!")
            print(f"File: {screenshot_file}")
            print("="*70)

            print("\nBrowser will close in 15 seconds...")
            await asyncio.sleep(15)

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
        success = asyncio.run(capture_applicant_name())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
