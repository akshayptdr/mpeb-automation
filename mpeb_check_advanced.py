#!/usr/bin/env python3
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

    print(f"[{timestamp}] Starting MPEB check (Advanced mode)...")

    async with async_playwright() as p:
        try:
            # Launch with anti-detection settings
            print("Launching browser with anti-detection settings...")
            browser = await p.chromium.launch(
                headless=False,  # Show browser so you can see it
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--single-process",
                    "--no-first-run",
                ]
            )

            page = await browser.new_page()

            # Masquerade as regular Chrome browser
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """)

            print("Navigating to MPEB website (this may take 30+ seconds)...")

            try:
                # Try with very long timeout
                await page.goto(
                    "https://mpwzservices.mpwin.co.in/mpeb_english/rtpfront",
                    timeout=60000,  # 60 seconds
                    wait_until="domcontentloaded"
                )
                print("Page loaded successfully!")
            except asyncio.TimeoutError:
                print("Page load timeout, but continuing anyway...")
            except Exception as e:
                print(f"Navigation error: {e}, continuing...")

            # Wait for user to complete the form
            await asyncio.sleep(3)
            print("\n" + "=" * 60)
            print("MANUAL STEPS REQUIRED:")
            print("=" * 60)
            print("\n1. In the browser window that opened:")
            print("   - Accept the terms and conditions")
            print("   - Enter IVRS number: N3330008565")
            print("   - Click Submit button")
            print("   - Wait for applicant name to appear")
            print("\n2. Come back to this terminal and press ENTER when done")
            print("=" * 60)

            # Block until user presses enter
            input("\nPress ENTER when you've completed the steps in the browser: ")

            # Check final state
            try:
                page_url = page.url
                print(f"\nFinal URL: {page_url}")
            except:
                pass

            # Log success
            status = "SUCCESS"
            message = "Manual verification completed"
            log_entry = f"[{timestamp}] {status}: {message}\n"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            print(f"Logged to {log_file}")

            print("\nBrowser will close in 5 seconds...")
            await asyncio.sleep(5)
            await browser.close()

            return True

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            log_entry = f"[{timestamp}] ERROR: {str(e)}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

            try:
                await browser.close()
            except:
                pass
            return False

if __name__ == "__main__":
    try:
        success = asyncio.run(check_mpeb_application())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
