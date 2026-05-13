
from playwright.sync_api import sync_playwright, expect

# Открываем браузер с использованием Playwright
with sync_playwright() as playwright:
    # Запускаем Chromium браузер в обычном режиме (не headless)
    browser = playwright.chromium.launch(headless=False)
    # Создаем новый контекст браузера (новая сессия, которая изолирована от других)
    context = browser.new_context()
    # Открываем новую страницу в рамках контекста
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

    page.wait_for_url("**/dashboard", timeout=10000)
    print("✅ Регистрация успешна")

   
    context.storage_state(path="browser-state.json")
    print("✅ Состояние сохранено")

    browser.close()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)

    context = browser.new_context(storage_state="browser-state.json")
    page = context.new_page()

    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses")

    page.wait_for_timeout(5000)

    # Проверить наличие и текст заголовка "Courses"
    courses_name = page.get_by_test_id('courses-list-toolbar-title-text')
    expect(courses_name).to_be_visible()

    # Проверить текст заголовка
    expect(courses_name).to_have_text("Courses")

    # Проверить наличие и текст блока "There is no results"

    no_results_text = page.get_by_test_id('courses-list-empty-view-title-text')
    expect(no_results_text).to_be_visible()

    expect(no_results_text).to_have_text("There is no results")

    # Проверить наличие и видимость иконки пустого блока  courses-list-empty-view-icon
    empty_icon = page.get_by_test_id('courses-list-empty-view-icon')
    expect(empty_icon).to_be_visible()

    # Проверить наличие и текст описания блока: "Results from the load test pipeline will be displayed here"
    description_text = page.get_by_test_id('courses-list-empty-view-description-text')
    expect(description_text).to_be_visible()
    expect(description_text).to_have_text("Results from the load test pipeline will be displayed here")



