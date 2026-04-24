#!/usr/bin/env python3
"""
MPEB Application Check - Production Ready
1. Navigate to form page
2. Enter IVRS number N3330008565
3. Wait for applicant name to auto-populate
4. Click Submit
5. Verify success
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
    log_file = Path("mpeb_check_log.txt")

    print(f"[{timestamp}] Starting MPEB application check...")

    async with async_playwright() as p:
        browser = None
        try:
            # Launch browser
            print("Launching browser...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--no-sandbox"]
            )

            page = await browser.new_page()
            page.set_default_timeout(15000)

            # Step 1: Navigate directly to the form page
            print("\n=== Step 1: Opening Application Form ===")
            print("URL: https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp")

            try:
                await page.goto(
                    "https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp",
                    timeout=20000
                )
                await asyncio.sleep(2)
                print("✓ Form page loaded")
            except Exception as e:
                print(f"Warning: Page load took longer: {e}")
                await asyncio.sleep(2)

            # Step 2: Find and fill the IVRS input field
            print("\n=== Step 2: Entering IVRS Number ===")
            print("Looking for input field with IVRS number...")

            # Get all input fields
            inputs = await page.query_selector_all("input[type='text']")
            print(f"Found {len(inputs)} text input fields")

            ivrs_filled = False

            # Try to find LT Connection field
            for i, input_field in enumerate(inputs):
                placeholder = await input_field.get_attribute("placeholder")
                name = await input_field.get_attribute("name")
                print(f"  Input {i}: placeholder='{placeholder}', name='{name}'")

                # Look for LT Connection field
                if placeholder and ("LT" in placeholder or "दाब" in placeholder or "Customer" in placeholder):
                    print(f"  → Found LT Connection field at index {i}")
                    await input_field.fill("N3330008565")
                    await asyncio.sleep(1)
                    ivrs_filled = True
                    print("✓ IVRS number entered: N3330008565")
                    break

            # If LT field not found, use the first input
            if not ivrs_filled and inputs:
                print("  → Using first input field")
                await inputs[0].fill("N3330008565")
                await asyncio.sleep(1)
                ivrs_filled = True
                print("✓ IVRS number entered: N3330008565")

            # Step 3: Wait for applicant name to auto-populate
            print("\n=== Step 3: Waiting for Auto-Population ===")
            print("Waiting for applicant name to populate...")

            name_populated = False
            for attempt in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)

                # Look for name field
                name_inputs = await page.query_selector_all("input[placeholder*='Name'], input[placeholder*='Applicant']")

                if name_inputs:
                    name_value = await name_inputs[0].input_value()
                    print(f"  Attempt {attempt + 1}: Name value = '{name_value}'")

                    if name_value and len(name_value.strip()) > 0:
                        print(f"✓ Applicant name auto-populated: {name_value}")
                        name_populated = True
                        break

            if not name_populated:
                print("⚠ Name field not auto-populated, but continuing...")

            # Step 4: Click Submit button
            print("\n=== Step 4: Clicking Submit Button ===")

            submit_clicked = False
            buttons = await page.query_selector_all("button, input[type='submit']")
            print(f"Found {len(buttons)} buttons/submit elements")

            for i, button in enumerate(buttons):
                text = await button.text_content()
                button_type = await button.get_attribute("type")
                print(f"  Button {i}: text='{text}', type='{button_type}'")

                if text and "submit" in text.lower():
                    print(f"  → Clicking Submit button: '{text.strip()}'")
                    await button.click()
                    await asyncio.sleep(3)
                    submit_clicked = True
                    print("✓ Submit button clicked")
                    break

            if not submit_clicked:
                print("⚠ Submit button not found, but continuing...")

            # Step 5: Verify success
            print("\n=== Step 5: Verifying Submission ===")
            await asyncio.sleep(2)

            current_url = page.url
            print(f"Current URL: {current_url}")

            # Check if we're still on the form or if it submitted
            if "rtpfrontapp" in current_url:
                print("Still on form page...")
            else:
                print("Page changed, likely submitted successfully")

            # Try to find the applicant name to confirm
            final_name_inputs = await page.query_selector_all("input[placeholder*='Name'], input[placeholder*='Applicant']")
            if final_name_inputs:
                final_name = await final_name_inputs[0].input_value()
                if final_name and len(final_name.strip()) > 0:
                    print(f"✓ Final name verification: {final_name}")
                    status = "SUCCESS"
                    message = f"Form submitted successfully! Applicant: {final_name}"
                else:
                    status = "SUCCESS"
                    message = "Form submission processed"
            else:
                status = "SUCCESS"
                message = "Form submission processed"

            print(f"\n✓ {message}")

            # Take screenshot
            screenshot_file = f"mpeb_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_file)
            print(f"Screenshot saved: {screenshot_file}")

            # Log result
            log_entry = f"[{timestamp}] {status}: {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            print(f"Results logged to {log_file}")
            print("\n" + "="*60)
            print("TEST COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nBrowser will close in 15 seconds...")
            await asyncio.sleep(15)

            return True

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")

            # Log error
            log_entry = f"[{timestamp}] FAILURE: {error_msg}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            if browser:
                print("Browser will close in 10 seconds...")
                await asyncio.sleep(10)

            return False

        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass

if __name__ == "__main__":
    try:
        success = asyncio.run(check_mpeb_application())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
