from playwright.sync_api import sync_playwright, expect

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/login")

    # Пытаемся проверить, что несуществующий локатор виден на странице
    unknown = page.locator('#unknown')
    expect(unknown).to_be_visible()
