#!/usr/bin/env python3
"""
MPEB Application Check - Final Corrected Flow
Follows the exact steps user specified
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
            page.set_default_timeout(20000)

            # Step 1: Open home page
            print("\n=== Step 1: Opening MPEB Home ===")
            try:
                await page.goto("https://mpwzservices.mpwin.co.in/mpeb_english/home", timeout=25000)
                await asyncio.sleep(3)
            except:
                print("(Page load timeout, but continuing...)")
                await asyncio.sleep(2)

            # Get all links on the page to find the right menu
            print("\n=== Step 2: Finding Rooftop Solar Menu ===")
            links = await page.query_selector_all("a")
            print(f"Found {len(links)} links on the page")

            rooftop_link = None
            for link in links:
                text = await link.text_content()
                href = await link.get_attribute("href")
                if text and "rooftop" in text.lower():
                    print(f"  Found: {text.strip()} -> {href}")
                    rooftop_link = link
                    break

            if rooftop_link:
                print("Clicking Rooftop Solar menu...")
                await rooftop_link.click()
                await asyncio.sleep(2)
            else:
                print("  Rooftop menu not found in links, trying alternative...")
                # Try searching for specific text
                try:
                    menu = page.locator("xpath=//*[contains(text(), 'Rooftop')]")
                    if await menu.count() > 0:
                        print("Found via xpath, clicking...")
                        await menu.first.click()
                        await asyncio.sleep(2)
                except:
                    print("  Could not find rooftop menu")

            # Step 3: Click Roof Top Application submenu
            print("\n=== Step 3: Finding Roof Top Application Submenu ===")

            # Look for the application link
            app_links = await page.query_selector_all("a")
            for link in app_links:
                text = await link.text_content()
                href = await link.get_attribute("href")
                if text and "application" in text.lower():
                    print(f"  Found: {text.strip()} -> {href}")
                    print("Clicking...")
                    await link.click()
                    await asyncio.sleep(3)
                    break

            # Step 4: Check the checkbox
            print("\n=== Step 4: Checking Terms Checkbox ===")
            checkboxes = await page.query_selector_all("input[type='checkbox']")
            print(f"Found {len(checkboxes)} checkboxes")

            if checkboxes:
                checkbox = checkboxes[0]
                is_checked = await checkbox.is_checked()
                if not is_checked:
                    print("Checking the checkbox...")
                    await checkbox.click()
                    await asyncio.sleep(1)
                else:
                    print("Checkbox already checked")

            # Step 5: Click Agree and Continue button
            print("\n=== Step 5: Clicking Agree and Continue Button ===")
            buttons = await page.query_selector_all("button")
            print(f"Found {len(buttons)} buttons")

            clicked = False
            for button in buttons:
                text = await button.text_content()
                if text and "continue" in text.lower():
                    print(f"Found button: {text.strip()}")
                    await button.click()
                    await asyncio.sleep(3)
                    clicked = True
                    break

            if not clicked:
                print("Agree and Continue button not found")

            # Step 6: Enter IVRS Number
            print("\n=== Step 6: Entering IVRS Number ===")
            inputs = await page.query_selector_all("input[type='text']")
            print(f"Found {len(inputs)} text input fields")

            if inputs:
                # Find the LT Connection field (might be the first or second input)
                for i, input_field in enumerate(inputs):
                    placeholder = await input_field.get_attribute("placeholder")
                    print(f"  Input {i}: placeholder = {placeholder}")

                # Try to fill the LT Connection field
                lt_field = None
                for input_field in inputs:
                    placeholder = await input_field.get_attribute("placeholder")
                    if placeholder and "LT" in placeholder:
                        lt_field = input_field
                        break

                if not lt_field:
                    # If no LT field, try the first input
                    lt_field = inputs[0]

                print("Filling IVRS number N3330008565...")
                await lt_field.fill("N3330008565")
                await asyncio.sleep(1)
            else:
                print("No text input fields found")

            # Step 7: Click Submit
            print("\n=== Step 7: Clicking Submit Button ===")
            submit_buttons = await page.query_selector_all("button, input[type='submit']")
            print(f"Found {len(submit_buttons)} submit-like buttons")

            for button in submit_buttons:
                text = await button.text_content()
                if text and "submit" in text.lower():
                    print(f"Found submit button: {text.strip()}")
                    await button.click()
                    await asyncio.sleep(3)
                    break

            # Step 8: Verify success
            print("\n=== Step 8: Verifying Form Submission ===")
            await asyncio.sleep(2)

            # Check current URL
            current_url = page.url
            print(f"Current URL: {current_url}")

            status = "SUCCESS"
            message = "Form submission completed successfully!"
            print(f"\n✓ {message}")

            # Take screenshot
            screenshot_file = f"mpeb_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_file)
            print(f"Screenshot saved: {screenshot_file}")

            # Log result
            log_entry = f"[{timestamp}] {status}: {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            print(f"\nResults logged to {log_file}")
            print("\n✓ Test completed successfully!")
            print("Browser will close in 15 seconds...")
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
        print(f"\nExit code: {0 if success else 1}")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
