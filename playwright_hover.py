from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    # Открываем браузер и создаем новую страницу
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    # Переходим на страницу входа
    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/login")

    # Находим ссылку Registration
    registration_link = page.get_by_test_id('login-page-registration-link')
    # Выполняем наведение курсора на ссылку
    registration_link.hover()

    # Добавляем паузу для наглядности результата
    page.wait_for_timeout(5000)
