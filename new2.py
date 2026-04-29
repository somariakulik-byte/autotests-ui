from playwright.sync_api import sync_playwright
import time


def test_connected():
    with sync_playwright() as p:
        try:
            # Подключаемся к уже запущенному браузеру
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Успешное подключение к браузеру!")

            # Берём первую активную вкладку
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            # Переходим на сайт (если ещё не перешли)
            if "LogonByDsKey" not in page.url:
                page.goto("http://dev-03.ru-central1.internal/Account/LogonByDsKey")

            # Проверяем, что плагин работает
            has_plugin = page.evaluate("typeof window.cadesplugin !== 'undefined'")
            print(f"🔐 Плагин ЭЦП: {'✅ найден' if has_plugin else '❌ не найден'}")

            # Ждём появления списка клиентов (подберите актуальный селектор!)
            try:
                page.wait_for_selector('.client-list, [data-testid="client-list"]', timeout=10000)
                print("✅ Список клиентов загружен!")
            except:
                print("⚠️ Селектор не найден, делаем скриншот для отладки")

            # Скриншот результата
            page.screenshot(path="connected_test.png")
            print("📸 Скриншот: connected_test.png")

            # Отключаемся (браузер останется открытым!)
            browser.close()

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("\n💡 Убедитесь, что браузер запущен с флагом:")
            print("   /Applications/Chromium-GOST.app/Contents/MacOS/Chromium-GOST --remote-debugging-port=9222")


if __name__ == "__main__":
    test_connected()