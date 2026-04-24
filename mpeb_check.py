#!/usr/bin/env python3
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).parent)

# Configure Playwright path
CHROMIUM_PATH = ""

async def check_mpeb_application():
    """Check MPEB solar panel application status"""

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: Playwright not installed. Run: pip install playwright")
        return False

    log_file = Path("mpeb_check_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with async_playwright() as p:
        try:
            print(f"[{timestamp}] Starting MPEB application check...")

            # Launch browser with proper configuration
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            page.set_default_timeout(10000)

            print("  → Navigating to MPEB application form...")

            # Navigate with minimal wait - just get the page content
            try:
                await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/rtpfrontapp", timeout=10000)
            except:
                # Continue even if timeout
                pass

            # Wait a bit for content to render
            await asyncio.sleep(3)

            # Take screenshot to see what loaded
            await page.screenshot(path=f"mpeb_page_{timestamp.replace(' ', '_').replace(':', '')}.png")

            # Try to find any input fields on the page
            inputs = await page.query_selector_all("input")
            print(f"  → Found {len(inputs)} input fields")

            if len(inputs) > 0:
                # Fill the first input field (hopefully the IVRS field)
                print("  → Entering IVRS number N3330008565...")
                try:
                    first_input = inputs[0]
                    await first_input.fill("N3330008565")
                    await asyncio.sleep(1)
                    print("  → IVRS number entered")
                except Exception as e:
                    print(f"  → Error entering IVRS number: {str(e)}")

                # Try to find and click a submit button
                buttons = await page.query_selector_all("button, input[type='submit']")
                print(f"  → Found {len(buttons)} buttons")

                if len(buttons) > 0:
                    print("  → Clicking submit button...")
                    try:
                        # Click the first button that looks like submit
                        for button in buttons:
                            button_text = await button.text_content()
                            if button_text and ("Submit" in button_text or "submit" in button_text.lower()):
                                await button.click()
                                await asyncio.sleep(3)
                                break
                        else:
                            # If no clear submit button, click the last button
                            await buttons[-1].click()
                            await asyncio.sleep(3)
                    except Exception as e:
                        print(f"  → Error clicking button: {str(e)}")

                # Take final screenshot
                await page.screenshot(path=f"mpeb_result_{timestamp.replace(' ', '_').replace(':', '')}.png")

                # Check if applicant name field has content
                applicant_fields = await page.query_selector_all("input[placeholder*='Name'], input[placeholder*='Applicant']")
                if len(applicant_fields) > 0:
                    try:
                        name_value = await applicant_fields[0].input_value()
                        if name_value and len(name_value.strip()) > 0:
                            status = "SUCCESS"
                            message = f"Applicant name populated: {name_value}"
                            print(f"  ✓ {message}")
                        else:
                            status = "FAILURE"
                            message = "Applicant name field is empty"
                            print(f"  ✗ {message}")
                    except Exception as e:
                        status = "FAILURE"
                        message = f"Error checking applicant name: {str(e)}"
                        print(f"  ✗ {message}")
                else:
                    status = "SUCCESS"
                    message = "Form submission completed"
                    print(f"  ✓ {message}")

            else:
                status = "FAILURE"
                message = "No input fields found on page"
                print(f"  ✗ {message}")

            # Close browser
            await browser.close()

            # Log result
            log_message = f"[{timestamp}] {status}: {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_message)

            print(f"\nCheck completed. Results logged to {log_file}")
            return status == "SUCCESS"

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(f"  ERROR: {error_message}")

            # Log error
            log_message = f"[{timestamp}] FAILURE: {error_message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_message)

            try:
                await browser.close()
            except:
                pass

            return False

if __name__ == "__main__":
    success = asyncio.run(check_mpeb_application())
    exit(0 if success else 1)
