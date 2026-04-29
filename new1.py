from playwright.sync_api import sync_playwright
import time


def diagnose():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="/Users/new/Library/Application Support/Chromium/Default",
            executable_path="/Applications/Chromium-GOST.app/Contents/MacOS/Chromium-GOST",
            headless=False
        )

        page = context.pages[0]
        page.goto("http://dev-03.ru-central1.internal/Account/LogonByDsKey")

        # Собираем информацию
        info = page.evaluate("""
                             () => {
                                 return {
                                     userAgent: navigator.userAgent,
                                     hasCadesPlugin: typeof window.cadesplugin !== 'undefined',
                                     cadesPluginType: typeof window.cadesplugin,
                                     platform: navigator.platform
                                 };
                             }
                             """)

        print(" Информация о браузере:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Скриншот
        page.screenshot(path="diagnose.png", full_page=True)
        print("📸 Скриншот: diagnose.png")

        time.sleep(10)
        context.close()


if __name__ == "__main__":
    diagnose()