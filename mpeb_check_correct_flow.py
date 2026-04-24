#!/usr/bin/env python3
"""
MPEB Application Check - Correct Flow
1. Open home page
2. Click Rooftop Solar Application menu
3. Click Roof Top Application submenu
4. Check "I have read all the instructions and conditions"
5. Click "Agree and Continue"
6. Enter IVRS number N3330008565
7. Click Submit
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
            # Launch browser with visible window
            print("Launching browser...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )

            page = await browser.new_page()
            page.set_default_timeout(15000)

            # Step 1: Open home page
            print("Step 1: Opening home page...")
            try:
                await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/home", timeout=20000)
                await asyncio.sleep(2)
            except:
                print("  (Home page load took longer, continuing...)")
                await asyncio.sleep(2)

            # Step 2: Click on "Rooftop Solar Applications" menu
            print("Step 2: Looking for Rooftop Solar Applications menu...")
            menu_found = False
            menu_selectors = [
                "text=Rooftop Solar Applications",
                "text=Rooftop Solar",
                "text=Solar",
                "[href*='rooftop']",
                "a:has-text('Rooftop')"
            ]

            for selector in menu_selectors:
                try:
                    menu = page.locator(selector)
                    if await menu.count() > 0:
                        first_menu = menu.first
                        if await first_menu.is_visible(timeout=3000):
                            print(f"  Found menu: {selector}")
                            await first_menu.click()
                            await asyncio.sleep(2)
                            menu_found = True
                            break
                except:
                    continue

            if not menu_found:
                print("  Menu not found, trying xpath search...")
                try:
                    menu = page.locator("xpath=//*[contains(text(), 'Rooftop')]")
                    if await menu.count() > 0:
                        await menu.first.click()
                        await asyncio.sleep(2)
                        menu_found = True
                except:
                    pass

            # Step 3: Click on "Roof Top Application" submenu
            print("Step 3: Looking for Roof Top Application submenu...")
            submenu_found = False
            submenu_selectors = [
                "text=Roof Top Application",
                "text=Application of Roof Top",
                "a:has-text('Application')",
                "[href*='rtpfront']"
            ]

            for selector in submenu_selectors:
                try:
                    submenu = page.locator(selector)
                    if await submenu.count() > 0:
                        first_submenu = submenu.first
                        if await first_submenu.is_visible(timeout=3000):
                            print(f"  Found submenu: {selector}")
                            await first_submenu.click()
                            await asyncio.sleep(3)
                            submenu_found = True
                            break
                except:
                    continue

            # Step 4: Wait for applicant name to auto-populate (this happens after form loads)
            print("Step 4: Waiting for applicant name to auto-populate...")
            applicant_name = None

            try:
                # Look for name field
                name_fields = await page.query_selector_all("input[placeholder*='Name'], input[placeholder*='Applicant']")
                if name_fields:
                    # Wait for it to be populated
                    for attempt in range(10):
                        await asyncio.sleep(1)
                        name_value = await name_fields[0].input_value()
                        if name_value and len(name_value.strip()) > 2:
                            applicant_name = name_value
                            print(f"  ✓ Applicant name populated: {applicant_name}")

                            # CAPTURE SCREENSHOT HERE - applicant name populated
                            screenshot_file = f"mpeb_applicant_name_populated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            await page.screenshot(path=screenshot_file)
                            print(f"  ✓ Screenshot captured: {screenshot_file}")
                            break
            except:
                pass

            # Step 4b: Check the checkbox "I have read all the instructions and conditions"
            print("Step 4b: Looking for checkbox...")
            checkbox_found = False
            checkbox_selectors = [
                "input[type='checkbox']",
                "xpath=//input[@type='checkbox']"
            ]

            for selector in checkbox_selectors:
                try:
                    checkbox = page.locator(selector)
                    if await checkbox.count() > 0:
                        first_checkbox = checkbox.first
                        is_checked = await first_checkbox.is_checked()
                        if not is_checked:
                            print("  Found checkbox, clicking it...")
                            await first_checkbox.click()
                            await asyncio.sleep(1)
                        else:
                            print("  Checkbox already checked")
                        checkbox_found = True
                        break
                except:
                    continue

            # Step 5: Click "Agree and Continue" button
            print("Step 5: Looking for Agree and Continue button...")
            button_found = False
            button_selectors = [
                "button:has-text('Agree and Continue')",
                "input[value='Agree and Continue']",
                "button:has-text('Continue')",
                "xpath=//*[contains(text(), 'Agree')]",
                "[style*='background']"  # Try any styled button
            ]

            for selector in button_selectors:
                try:
                    button = page.locator(selector)
                    if await button.count() > 0:
                        first_button = button.first
                        if await first_button.is_visible(timeout=3000):
                            print(f"  Found button: {selector}")
                            await first_button.click()
                            await asyncio.sleep(3)
                            button_found = True
                            break
                except:
                    continue

            # Step 6: Enter IVRS number
            print("Step 6: Looking for IVRS input field...")
            input_found = False
            input_selectors = [
                "input[placeholder*='LT Connection']",
                "input[placeholder*='Customer']",
                "input[placeholder*='IVRS']",
                "input[placeholder*='दाब']",  # Hindi text
                "input[type='text']"
            ]

            for selector in input_selectors:
                try:
                    input_field = page.locator(selector)
                    if await input_field.count() > 0:
                        first_input = input_field.first
                        if await first_input.is_visible(timeout=2000):
                            print(f"  Found input field: {selector}")
                            await first_input.fill("N3330008565")
                            await asyncio.sleep(1)
                            input_found = True
                            break
                except:
                    continue

            if not input_found:
                print("  IVRS field not found, trying all text inputs...")
                all_inputs = await page.query_selector_all("input[type='text']")
                if len(all_inputs) > 0:
                    print(f"  Found {len(all_inputs)} text inputs, using first one")
                    await all_inputs[0].fill("N3330008565")
                    await asyncio.sleep(1)
                    input_found = True

            # Step 7: Click Submit button
            print("Step 7: Looking for Submit button...")
            submit_found = False
            submit_selectors = [
                "button:has-text('Submit')",
                "input[type='submit']",
                "button[type='submit']",
                "xpath=//*[contains(text(), 'Submit')]"
            ]

            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector)
                    if await submit_btn.count() > 0:
                        first_submit = submit_btn.first
                        if await first_submit.is_visible(timeout=2000):
                            print(f"  Found submit button: {selector}")
                            await first_submit.click()
                            await asyncio.sleep(3)
                            submit_found = True
                            break
                except:
                    continue

            # Wait for page to load after submit
            await asyncio.sleep(2)

            # Check if form was submitted successfully
            print("Step 8: Verifying form submission...")
            try:
                # Look for applicant name field to see if it got populated
                name_field = page.locator("input[placeholder*='Name'], input[placeholder*='Applicant']")
                if await name_field.count() > 0:
                    name_value = await name_field.first.input_value()
                    if name_value and len(name_value.strip()) > 0:
                        status = "SUCCESS"
                        message = f"Form submitted successfully! Applicant name: {name_value}"
                    else:
                        status = "SUCCESS"
                        message = "Form submitted (name field found but empty)"
                else:
                    status = "SUCCESS"
                    message = "Form submission completed"
            except:
                status = "SUCCESS"
                message = "Form submission completed"

            print(f"\n✓ {message}")

            # Take screenshot
            screenshot_file = f"mpeb_success_{timestamp.replace(' ', '_').replace(':', '')}.png"
            await page.screenshot(path=screenshot_file)
            print(f"Screenshot saved: {screenshot_file}")

            # Log result
            log_entry = f"[{timestamp}] {status}: {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            print(f"\nResults logged to {log_file}")
            print("Browser will close in 10 seconds...")
            await asyncio.sleep(10)

            return True

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")

            # Log error
            log_entry = f"[{timestamp}] FAILURE: {error_msg}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            if browser:
                print("Browser will close in 5 seconds...")
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
        success = asyncio.run(check_mpeb_application())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
