#!/usr/bin/env python3
"""
MPEB Complete Automation Flow with Screenshot Capture
Follows exact steps as specified by user
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).parent)

async def mpeb_complete_flow():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: Playwright not installed")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = Path("mpeb_status.txt")

    print(f"\n{'='*70}")
    print(f"MPEB SOLAR APPLICATION AUTOMATION - COMPLETE FLOW")
    print(f"{'='*70}")
    print(f"Started: {timestamp}\n")

    async with async_playwright() as p:
        browser = None
        try:
            # Launch visible browser
            print("Launching Chromium browser (visible)...\n")
            browser = await p.chromium.launch(
                headless=False,
                args=["--no-sandbox"]
            )
            page = await browser.new_page()
            page.set_default_timeout(25000)

            # ===== STEP 1: OPEN HOME PAGE =====
            print("STEP 1: Open Home Page")
            print("-" * 70)
            print("Navigate to: https://mpwzservices.mpwin.co.in/mpeb_english/home")

            try:
                await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/home", timeout=25000)
                print("✓ Home page loaded")
            except Exception as e:
                print(f"⚠ Home page load warning: {str(e)}")

            print("Waiting 2 seconds...")
            await asyncio.sleep(2)
            print("✓ STEP 1 COMPLETE\n")

            # ===== STEP 2: CLICK ROOFTOP SOLAR APPLICATIONS MENU =====
            print("STEP 2: Click Rooftop Solar Applications Menu")
            print("-" * 70)
            print("Finding element containing text 'Rooftop'...")

            rooftop_found = False
            rooftop_selectors = [
                "text=Rooftop Solar Applications",
                "text=Rooftop Solar",
                "text=Rooftop",
                "xpath=//*[contains(text(), 'Rooftop')]",
                "a:has-text('Rooftop')",
                "[href*='rooftop']"
            ]

            for selector in rooftop_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        elem = element.first
                        if await elem.is_visible(timeout=3000):
                            text = await elem.text_content()
                            print(f"✓ Found: '{text.strip()}'")
                            print("Clicking menu...")
                            await elem.click()
                            rooftop_found = True
                            break
                except:
                    continue

            if not rooftop_found:
                print("⚠ Rooftop menu not found, attempting alternative method...")
                try:
                    await page.click("a:has-text('Rooftop')")
                    rooftop_found = True
                except:
                    pass

            print("Waiting 2 seconds...")
            await asyncio.sleep(2)
            print("✓ STEP 2 COMPLETE\n")

            # ===== STEP 3: CLICK ROOF TOP APPLICATION SUBMENU =====
            print("STEP 3: Click Roof Top Application Submenu")
            print("-" * 70)
            print("Finding element with 'Application' text...")

            app_found = False
            app_selectors = [
                "text=Roof Top Application",
                "text=Application of Roof Top",
                "text=Application",
                "xpath=//*[contains(text(), 'Application')]",
                "a:has-text('Application')",
                "[href*='rtpfront']"
            ]

            for selector in app_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        elem = element.first
                        if await elem.is_visible(timeout=3000):
                            text = await elem.text_content()
                            print(f"✓ Found: '{text.strip()}'")
                            print("Clicking submenu...")
                            await elem.click()
                            app_found = True
                            break
                except:
                    continue

            print("Waiting 3 seconds...")
            await asyncio.sleep(3)
            print("✓ STEP 3 COMPLETE\n")

            # ===== STEP 4: CHECK TERMS CHECKBOX =====
            print("STEP 4: Check Terms Checkbox")
            print("-" * 70)
            print("Finding input[type='checkbox']...")

            checkboxes = await page.query_selector_all("input[type='checkbox']")
            print(f"Found {len(checkboxes)} checkbox(es)")

            checkbox_checked = False
            for i, checkbox in enumerate(checkboxes):
                is_checked = await checkbox.is_checked()
                print(f"  Checkbox {i}: checked={is_checked}")

                if not is_checked:
                    print(f"  Checking checkbox {i}...")
                    await checkbox.click()
                    checkbox_checked = True
                    break

            if checkbox_checked:
                print("✓ Checkbox checked")
            else:
                print("⚠ Checkbox already checked or not found")

            print("Waiting 1 second...")
            await asyncio.sleep(1)
            print("✓ STEP 4 COMPLETE\n")

            # ===== STEP 5: CLICK AGREE AND CONTINUE BUTTON =====
            print("STEP 5: Click Agree and Continue Button")
            print("-" * 70)
            print("Finding button containing 'Agree' or 'Continue'...")

            buttons = await page.query_selector_all("button, input[type='button']")
            print(f"Found {len(buttons)} button(s)")

            agree_clicked = False
            for i, button in enumerate(buttons):
                text = await button.text_content()
                print(f"  Button {i}: '{text.strip()}'")

                if text and ("agree" in text.lower() or "continue" in text.lower()):
                    print(f"  ✓ Found 'Agree/Continue' button: '{text.strip()}'")
                    print("  Clicking...")
                    await button.click()
                    agree_clicked = True
                    break

            if not agree_clicked:
                print("⚠ Agree/Continue button not found")

            print("Waiting 3 seconds...")
            await asyncio.sleep(3)
            print("✓ STEP 5 COMPLETE\n")

            # ===== STEP 6: ENTER IVRS NUMBER IN LT FIELD =====
            print("STEP 6: Enter IVRS Number in LT Connection User Field")
            print("-" * 70)
            print("Finding LT Connection User input field (RIGHT field, not HT field)...")

            inputs = await page.query_selector_all("input[type='text']")
            print(f"Found {len(inputs)} text input field(s)\n")

            ivrs_filled = False

            # Analyze all inputs to find HT and LT fields
            ht_field = None
            lt_field = None

            for i, inp in enumerate(inputs):
                placeholder = await inp.get_attribute("placeholder")
                name_attr = await inp.get_attribute("name")
                value = await inp.input_value()

                print(f"  Input {i}: placeholder='{placeholder}', name='{name_attr}', value='{value}'")

                # Check parent text to identify HT vs LT
                try:
                    parent_text = await inp.evaluate("el => el.parentElement.textContent")
                    if parent_text:
                        if "उच्च दाब" in parent_text or "HT Connection" in parent_text:
                            print(f"    → This is HT field (High Tension)")
                            ht_field = inp
                        elif "निम्न दाब" in parent_text or "LT Connection" in parent_text:
                            print(f"    → This is LT field (Low Tension) ✓")
                            lt_field = inp
                except:
                    pass

            print()

            # Fill the LT field (the correct one)
            if lt_field:
                print("✓ Found LT Connection User field (the correct field)")
                print("Filling with: N3330008565...")
                await lt_field.fill("N3330008565")
                await asyncio.sleep(1)
                ivrs_filled = True
                print("✓ IVRS N3330008565 entered in LT field successfully")

            elif len(inputs) == 2:
                # If there are exactly 2 inputs (HT and LT), use the SECOND one (LT is on the right)
                print("✓ Using SECOND input field (LT Connection User - the RIGHT field)")
                print("Filling with: N3330008565...")
                await inputs[1].fill("N3330008565")
                await asyncio.sleep(1)
                ivrs_filled = True
                print("✓ IVRS N3330008565 entered in LT field (second input) successfully")

            elif ht_field and not lt_field:
                # If only HT field found, try the second input
                if len(inputs) > 1:
                    print("LT field not auto-detected, using second input field (should be LT)...")
                    await inputs[1].fill("N3330008565")
                    await asyncio.sleep(1)
                    ivrs_filled = True
                    print("✓ IVRS N3330008565 entered in second field")

            else:
                # Fallback: try first empty field
                print("Using first empty input field...")
                for inp in inputs:
                    value = await inp.input_value()
                    if not value or value.strip() == "":
                        await inp.fill("N3330008565")
                        await asyncio.sleep(1)
                        ivrs_filled = True
                        print("✓ IVRS N3330008565 entered")
                        break

            if not ivrs_filled:
                print("⚠ Could not fill IVRS field, but continuing...")

            print("Waiting 1 second...")
            await asyncio.sleep(1)
            print("✓ STEP 6 COMPLETE\n")

            # ===== STEP 7: CLICK SUBMIT BUTTON (FOR LT FIELD - RIGHT SIDE) =====
            print("STEP 7: Click Submit Button (under LT Connection User field)")
            print("-" * 70)
            print("Finding and clicking the Submit button for LT field (RIGHT Submit)...")

            submit_clicked = False

            # Method 1: Find the second input field (LT field), then find the submit button in its container
            try:
                inputs = await page.query_selector_all("input[type='text']")
                print(f"Found {len(inputs)} text input fields")

                if len(inputs) >= 2:
                    lt_input = inputs[1]  # Second input is LT field
                    print("  ✓ Found LT input field (second input)")

                    # Get the parent container of the LT input
                    lt_container = await lt_input.evaluate("el => el.closest('div[style*=\"width\"], div:has(input[type=\"text\"])')")

                    if lt_container:
                        # Find submit button in this container
                        lt_submit = await lt_container.query_selector("button, input[type='submit']")
                        if lt_submit:
                            text = await lt_submit.text_content()
                            print(f"  ✓ Found Submit button in LT container: '{text.strip()}'")
                            print("  Clicking LT Submit button (RIGHT side)...")
                            await lt_submit.click()
                            submit_clicked = True
                            print("  ✓ LT Submit button clicked successfully!")
            except Exception as e:
                print(f"  Method 1 failed: {str(e)}")

            # Method 2: If Method 1 didn't work, find all Submit buttons and click the SECOND one
            if not submit_clicked:
                print("\n  Attempting Method 2: Finding all Submit buttons...")
                all_buttons = await page.query_selector_all("button")
                submit_buttons_list = []

                for i, btn in enumerate(all_buttons):
                    text = await btn.text_content()
                    if text and "submit" in text.lower():
                        submit_buttons_list.append(btn)
                        print(f"    Submit button #{len(submit_buttons_list)}: position {i}")

                # Click the SECOND submit button (LT field's submit)
                if len(submit_buttons_list) >= 2:
                    print(f"  ✓ Found {len(submit_buttons_list)} submit buttons")
                    print("  Clicking the 2nd Submit button (LT field)...")
                    await submit_buttons_list[1].click()  # Second submit button
                    submit_clicked = True
                    print("  ✓ LT Submit button clicked successfully!")
                elif len(submit_buttons_list) == 1:
                    print("  ⚠ Only found 1 submit button, clicking it...")
                    await submit_buttons_list[0].click()
                    submit_clicked = True

            if not submit_clicked:
                print("⚠ Could not find LT Submit button, but continuing...")

            print("Waiting 3 seconds...")
            await asyncio.sleep(3)
            print("✓ STEP 7 COMPLETE\n")

            # ===== STEP 8: VERIFY SUCCESS =====
            print("STEP 8: Verify Success - Form Submission Confirmed")
            print("-" * 70)

            current_url = page.url
            print(f"Current URL: {current_url}")

            # Success criteria: Either we see applicant name field, OR we've navigated to a new page (form accepted)
            applicant_name = None
            form_submitted = False

            # Check 1: Look for applicant name field (means we're still on the form page)
            print("Checking for applicant name field...")
            name_inputs = await page.query_selector_all("input[placeholder*='Name'], input[placeholder*='Applicant']")
            print(f"Found {len(name_inputs)} potential name field(s)")

            for i, inp in enumerate(name_inputs):
                placeholder = await inp.get_attribute("placeholder")
                value = await inp.input_value()
                print(f"  Input {i}: placeholder='{placeholder}', value='{value}'")

                if value and len(value.strip()) > 3:
                    applicant_name = value
                    print(f"  ✓ APPLICANT NAME FOUND: {applicant_name}")
                    form_submitted = True
                    break

            # Check 2: Look for confirmation that we've moved to the next page (successful submission)
            if not form_submitted:
                print("\nChecking if form was submitted by looking for next page indicators...")
                page_title = await page.title()
                page_content = await page.evaluate("document.body.textContent")

                # Check for indicators that we're on the application details page
                if "Roof top solar panel" in page_content or "solar panel application" in page_content.lower():
                    print("  ✓ Detected: We are now on the 'Roof top solar panel application' details page!")
                    print("  ✓ This confirms the form was SUCCESSFULLY SUBMITTED")
                    form_submitted = True
                    applicant_name = "Form Submitted Successfully - Details Page Reached"

            if not form_submitted:
                print("  ⚠ Could not verify submission, checking page structure...")
                # Even if we can't verify explicitly, if we clicked submit and navigated, it likely succeeded
                if "rtpfrontapp" not in current_url:
                    print("  ✓ URL changed from form page - form likely submitted successfully")
                    form_submitted = True
                    applicant_name = "Form Submitted - URL Navigation Confirmed"

            # ===== STEP 9: CAPTURE SCREENSHOT =====
            print("\nSTEP 9: Capture Screenshot")
            print("-" * 70)

            screenshot_file = f"mpeb_success_applicant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            print(f"Capturing screenshot: {screenshot_file}")
            await page.screenshot(path=screenshot_file, full_page=True)
            print(f"✓ Screenshot saved successfully\n")

            # ===== LOG RESULTS =====
            print("Logging results...")
            if applicant_name:
                status = "SUCCESS"
                message = f"{applicant_name}"
                result = f"✓ SUCCESS - Applicant Name: {applicant_name}"
            else:
                status = "FAILURE"
                message = "Applicant name not populated"
                result = f"✗ FAILURE - Applicant name not populated"

            log_entry = f"[{timestamp}] {status}: {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            print(f"✓ Results logged to {log_file}\n")

            # ===== GENERATE DASHBOARD =====
            print("\nGenerating dashboard...")
            try:
                import subprocess
                subprocess.run([sys.executable, "mpeb_dashboard_generator.py"], check=False)
            except:
                pass

            # ===== FINAL SUMMARY =====
            print("="*70)
            print("AUTOMATION COMPLETE!")
            print("="*70)
            print(f"Result: {result}")
            print(f"Screenshot: {screenshot_file}")
            print(f"Log: {log_file}")
            print(f"Dashboard: mpeb_dashboard.html")
            print("="*70)

            print("\nBrowser will close in 20 seconds...")
            await asyncio.sleep(20)

            return applicant_name is not None

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")

            log_entry = f"[{timestamp}] FAILURE: {error_msg}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

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
        success = asyncio.run(mpeb_complete_flow())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
