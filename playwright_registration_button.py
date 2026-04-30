from playwright.sync_api import sync_playwright, expect

from playwright_registration import registration_button

with sync_playwright() as playwright:
    # Открываем браузер и создаем новую страницу
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    # Переходим на страницу входа
    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration")

    # Проверить, что кнопка "Registration"  находится в состоянии disabled
    registration_button = page.get_by_test_id('registration-page-registration-button')
    expect(registration_button).to_be_disabled


    # Заполнить поле Email значением: user.name @ gmail.com.
    email_input = page.get_by_test_id('registration-form-email-input').locator('input')
    email_input.fill("user.name@gmail.com")

    # Заполнить поле Username значением: username.
    username_input = page.get_by_test_id('registration-form-username-input').locator('input')
    username_input.fill("username")

    # Заполнить поле Password значением: password.
    password_input = page.get_by_test_id('registration-form-password-input').locator('input')
    password_input.fill("password")

    # Проверить, что кнопка "Registration" перешла в   состояние  enabled
    expect(registration_button).to_be_enabled

