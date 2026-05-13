from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    # Регистрация
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration")

    email_input = page.get_by_test_id('registration-form-email-input').locator('input')
    email_input.fill('user.name@gmail.com')

    username_input = page.get_by_test_id('registration-form-username-input').locator('input')
    username_input.fill('username')

    password_input = page.get_by_test_id('registration-form-password-input').locator('input')
    password_input.fill('password')

    registration_button = page.get_by_test_id('registration-page-registration-button')
    registration_button.click()

    # Ожидаем редирект или появление элемента на дашборде
    page.wait_for_url("**/dashboard")

    # Сохраняем состояние
    context.storage_state(path="browser-state.json")

    # Переиспользуем ту же страницу или создаем новую
    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/dashboard")

    # Проверяем, что мы на дашборде
    assert page.url.endswith("/dashboard")

    page.wait_for_timeout(5000)
