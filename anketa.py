from playwright.sync_api import sync_playwright, Page
import time
from functools import wraps
from typing import Optional


# ============================================================================
# ⚙️ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ-ОБЕРТКИ
# ============================================================================

def safe_action(func):
    """Декоратор для безопасного выполнения действий с обработкой ошибок"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ {func.__name__}: {e}")
            return False

    return wrapper


def safe_fill(page: Page, selector: str, value: str, field_name: str, timeout: int = 10000) -> bool:
    """Безопасное заполнение поля"""
    try:
        field = page.locator(selector).first
        field.wait_for(state='visible', timeout=timeout)
        field.scroll_into_view_if_needed()
        field.click()
        field.clear()
        field.fill(value)
        print(f"✅ {field_name} заполнен")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось заполнить {field_name}: {e}")
        return False


def safe_click(page: Page, selector: str, field_name: str, timeout: int = 10000) -> bool:
    """Безопасное нажатие кнопки"""
    try:
        btn = page.locator(selector).first
        btn.wait_for(state='visible', timeout=timeout)
        btn.scroll_into_view_if_needed()
        btn.click()
        print(f"✅ {field_name} нажат")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось нажать {field_name}: {e}")
        return False


def safe_check(page: Page, selector: str, field_name: str, timeout: int = 10000) -> bool:
    """Безопасный выбор радиокнопки"""
    try:
        radio = page.locator(selector).first
        radio.wait_for(state='visible', timeout=timeout)
        radio.scroll_into_view_if_needed()
        radio.check()
        print(f"✅ {field_name} выбран")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось выбрать {field_name}: {e}")
        return False


def set_datepicker(page: Page, selector: str, field_name: str, year: int, month: int, day: int) -> bool:
    """Установка даты через jQuery datepicker"""
    try:
        page.evaluate(f'''
            (function() {{
                var dateField = document.querySelector('{selector}');
                if (dateField && typeof jQuery !== 'undefined' && jQuery(dateField).datepicker) {{
                    jQuery(dateField).datepicker('setDate', new Date({year}, {month}, {day}));
                    jQuery(dateField).change();
                }} else if (dateField) {{
                    dateField.value = '{day:02d}.{month + 1:02d}.{year}';
                    dateField.dispatchEvent(new Event('change', {{bubbles: true}}));
                    dateField.dispatchEvent(new Event('blur', {{bubbles: true}}));
                }}
            }})();
        ''')
        page.wait_for_timeout(1000)
        print(f"✅ {field_name} заполнена")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось заполнить {field_name}: {e}")
        return False


def safe_upload_file(page: Page, selector: str, file_path: str, field_name: str) -> bool:
    """Безопасная загрузка файла"""
    try:
        with page.expect_file_chooser() as fc_info:
            page.locator(selector).click()
        fc_info.value.set_files(file_path)
        print(f"✅ {field_name} загружен")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {field_name}: {e}")
        return False


def switch_to_tab(page: Page, tab_selector: str, tab_name: str) -> bool:
    """Переключение на вкладку"""
    try:
        page.click(tab_selector, timeout=10000)
        page.wait_for_timeout(1500)
        print(f"✅ Вкладка '{tab_name}' активна")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось перейти на вкладку '{tab_name}': {e}")
        return False


# ============================================================================
# 🔐 ФУНКЦИИ АВТОРИЗАЦИИ
# ============================================================================

def login_agent(page: Page) -> bool:
    """Выполняет вход в систему как агент"""
    print("🔗 Кликаем 'Вход для агентов'...")
    if not safe_click(page, 'text=Вход для агентов', "Вход для агентов"):
        return False

    print("📝 Заполняем форму...")
    page.wait_for_selector('#Email', state='visible', timeout=15000)
    page.fill('#Email', 'akinfeev@mail.ru')
    page.fill('#Password', '1q2w!Q@W')
    safe_click(page, 'button:has-text("Войти")', "Кнопка Войти")
    page.wait_for_load_state("networkidle", timeout=30000)
    print("✅ Вход выполнен")
    return True


# ============================================================================
# 🏢 ФУНКЦИИ РАБОТЫ С КЛИЕНТАМИ
# ============================================================================

def get_inn_from_user() -> str:
    """Запрашивает ИНН у пользователя через консоль"""
    print("\n" + "=" * 50)
    inn = input("🔢 ВВЕДИТЕ ИНН клиента и нажмите Enter: ").strip()
    print("=" * 50 + "\n")
    return inn


def determine_client_type(inn: str) -> str:
    """Определяет тип клиента по длине ИНН"""
    if len(inn) == 12:
        return "individual"
    elif len(inn) == 10:
        return "legal_entity"
    return "unknown"


def fill_inn_field(page: Page, inn: str) -> None:
    """Заполняет поле ИНН и снимает фокус"""
    print("🔢 Заполняем поле ИНН...")
    page.locator('#newClientModal input.controls.mywidth').fill(inn)
    page.keyboard.press('Tab')
    time.sleep(1)
    print(f"✅ ИНН {inn} заполнен")


def click_continue_button(page: Page) -> bool:
    """Нажимает кнопку 'Продолжить' после валидации ИНН"""
    print("⏳ Ждём активации кнопки 'Продолжить'...")
    continue_btn = page.locator('#newClientModal button.btn-primary')
    continue_btn.wait_for(state='visible', timeout=10000)

    if continue_btn.is_disabled():
        page.click('#newClientModal .modal-header', timeout=5000)
        time.sleep(1)
        if continue_btn.is_disabled():
            print("❌ Кнопка заблокирована")
            return False

    continue_btn.click(timeout=10000)
    page.wait_for_load_state("networkidle", timeout=30000)
    print("✅ 'Продолжить' нажата")
    return True


# ============================================================================
# 📝 ФУНКЦИИ ЗАПОЛНЕНИЯ ДЛЯ ФИЗЛИЦА
# ============================================================================

def fill_egrip_tab(page: Page) -> None:
    """Загружает файлы на вкладке 'ЕГРИП'"""
    print("📋 Начинаем загрузку файлов на вкладке 'ЕГРИП'...")
    safe_upload_file(page, '#TaxDepRegistrationFile .select-link', "/Users/new/Documents/ИП_учет.jpeg", "ИП_учет.jpeg")
    safe_upload_file(page, '#GovRegistrationFile .select-link', "/Users/new/Documents/ИП_госрег.jpeg", "ИП_госрег.jpeg")
    print("✅ Файлы на вкладке ЕГРИП загружены")


def fill_questionnaire_tab(page: Page) -> bool:
    """Заполняет вкладку 'Опросный лист' для физлица"""
    print("📋 Начинаем заполнение вкладки 'Опросный лист'...")
    if not switch_to_tab(page, '.tab[content="tab-content-questionnaire"]', "Опросный лист"):
        return False

    address_fields = [
        ('[data-bind*="QuestionnaireData.AddressIndexElement"] input', "115404", "Индекс"),
        ('[data-bind*="QuestionnaireData.RegionElement"] input', "Московская", "Область"),
        ('[data-bind*="QuestionnaireData.DistrictElement"] input', "Москва", "Район"),
        ('[data-bind*="QuestionnaireData.LocalityTypeElement"] input', "Москва", "Населенный пункт"),
        ('[data-bind*="QuestionnaireData.StreetElement"] input', "Горчакова", "Улица"),
        ('[data-bind*="QuestionnaireData.HouseElement"] input', "5", "Дом"),
        ('[data-bind*="QuestionnaireData.ApartmetElement"] input', "10", "Квартира"),
    ]

    for selector, value, name in address_fields:
        safe_fill(page, selector, value, name)

    # Строение (опционально)
    try:
        page.locator('[data-bind*="QuestionnaireData.BuildingElement"] input').fill("-")
        print("✅ Строение пропущено")
    except:
        print("⏭ Поле 'Строение' не найдено")

    # Переключатели и счет
    safe_check(page, 'input[name="haveDerzhavaAccountOptions"][value="0"]', "Да (счет в Державе)")
    safe_fill(page, '#BankDerzhavaAccount', "40702810949770029722", "Расчетный счет")
    page.keyboard.press('Tab')
    page.wait_for_timeout(1000)

    safe_check(page, 'input[name="haveLocalBankAccountsOptions"][value="1"]', "Нет (счета в локальных банках)")
    safe_fill(page, '#QuestionnairePhone', "9102568574", "Телефон")
    safe_fill(page, '[data-bind*="QuestionnaireData.EmailElement"] input', "test@mail.ru", "Email")

    print("✅ Вкладка 'Опросный лист' полностью заполнена!")
    return True


def fill_physical_person_tab(page: Page) -> bool:
    """Заполняет вкладку 'Физическое лицо'"""
    print("📋 Начинаем заполнение вкладки 'Физическое лицо'...")
    if not switch_to_tab(page, '.tab[content="tab-content-physicalpersons"]', "Физическое лицо"):
        return False

    safe_click(page, 'button:has-text("Редактировать")', "Кнопка Редактировать")
    page.wait_for_timeout(2000)

    safe_fill(page, '#Series-0', "4515", "Серия")
    safe_fill(page, '#Number-0', "152452", "Номер")
    set_datepicker(page, '#IssueDateElement-1', "Дата выдачи", 2026, 3, 1)
    safe_fill(page, '#DepartmentCode-1', "515-215", "Код подразделения")

    # Выдан кем
    try:
        issued_by_field = page.locator('[data-bind*="Issuer"] input:visible:not([disabled])').first
        issued_by_field.fill("ОВА Мичуринского района")
        print("✅ 'Выдан кем' заполнено")
    except Exception as e:
        print(f"⚠️ Не удалось заполнить 'Выдан кем': {e}")

    set_datepicker(page, '#BirthDateElement-1', "Дата рождения", 2012, 3, 1)
    safe_fill(page, 'div[data-bind*="BirthPlace"] .data-container input', "Москва", "Место рождения")
    safe_fill(page, 'div[data-bind*="RegAddress"] .data-container input', "Москва, ул. Тверская, д. 13",
              "Адрес регистрации")
    safe_fill(page, 'div[data-bind*="ActualAddress"] .data-container input', "Москва, ул. Тверская, д. 13",
              "Адрес фактического пребывания")
    print("💾 Нажимаем кнопку 'Сохранить'...")

    save_button_clicked = False

    # Вариант 1: Поиск по точному тексту с force=True
    try:
        save_btn = page.get_by_role("button", name="Сохранить", exact=True)
        if save_btn.count() > 0:
            save_btn.scroll_into_view_if_needed()
            save_btn.click(force=True)
            print("✅ Кнопка 'Сохранить' нажата (force click)")
            save_button_clicked = True
    except Exception as e:
        print(f"   Вариант 1 не сработал: {e}")

    print("✅ Вкладка 'Физическое лицо' заполнена!")
    return True


# ============================================================================
# 🏢 ФУНКЦИИ ЗАПОЛНЕНИЯ ДЛЯ ЮРЛИЦА
# ============================================================================

def fill_legal_entity_questionnaire_tab(page: Page) -> bool:
    """Заполняет вкладку 'Опросный лист' для юрлица"""
    print("📋 Начинаем заполнение вкладки 'Опросный лист' (юрлицо)...")
    if not switch_to_tab(page, '.tab[content="tab-content-questionnaire"]', "Опросный лист"):
        return False

    set_datepicker(page, '#managerOccupationStartDate-0', "Дата назначения", 2026, 3, 1)
    safe_fill(page, '#WorkExperience-0', "5", "Работа в отрасли")

    # Предыдущее место работы
    try:
        container = page.locator('.label-container:has-text("Предыдущее место работы")').locator('..')
        container.locator('.data-container input').fill("ООО «Мир»")
        print("✅ 'Предыдущее место работы' заполнено")
    except Exception as e:
        print(f"⚠️ Не удалось заполнить 'Предыдущее место работы': {e}")

    safe_check(page, 'input[name="NoCollegialManagement"]', "Отсутствует (коллегиальный орган)")

    page.locator('h3:has-text("Информация об открытых расчетных счетах")').scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    safe_check(page, 'input[name="haveDerzhavaAccountOptions"][value="0"]', "Да (счет в Державе)")
    safe_fill(page, '#BankDerzhavaAccount', "40702810949770029722", "Расчетный счет")
    page.keyboard.press('Tab')
    page.wait_for_timeout(1000)

    safe_check(page, 'input[name="haveLocalBankAccountsOptions"][value="1"]', "Нет (счета в локальных банках)")
    safe_fill(page, '#QuestionnairePhone', "9102568574", "Телефон")
    safe_fill(page, '[data-bind*="QuestionnaireData.EmailElement"] input', "rocket@list.ru", "Email")

    print("✅ Вкладка 'Опросный лист' (юрлицо) заполнена!")
    return True


def fill_legal_entity_physical_persons_tab(page: Page) -> bool:
    """Заполняет вкладку 'Физические лица' для юрлица"""
    print("📋 Начинаем заполнение вкладки 'Физические лица' (юрлицо)...")
    if not switch_to_tab(page, '.tab[content="tab-content-physicalpersons"]', "Физические лица"):
        return False

    safe_click(page, 'button:has-text("Редактировать")', "Кнопка Редактировать")
    page.wait_for_timeout(2000)

    safe_upload_file(page, '#DocumentScan-1 .select-link', "/Users/new/Documents/паспорт.jpg", "Скан паспорта")
    safe_fill(page, '#Series-0', "4515", "Серия")
    safe_fill(page, '#Number-0', "152452", "Номер")
    set_datepicker(page, '#IssueDateElement-1', "Дата выдачи", 2026, 3, 1)
    safe_fill(page, '#DepartmentCode-1', "515-215", "Код подразделения")

    # Выдан кем
    try:
        issued_by_field = page.locator('[data-bind*="Issuer"] input:visible:not([disabled])').first
        issued_by_field.fill("ОВД Мичуринского района")
        print("✅ 'Выдан кем' заполнено")
    except Exception as e:
        print(f"⚠️ Не удалось заполнить 'Выдан кем': {e}")

    set_datepicker(page, '#BirthDateElement-1', "Дата рождения", 2012, 3, 1)
    safe_fill(page, 'div[data-bind*="BirthPlace"] .data-container input', "Москва", "Место рождения")
    safe_fill(page, '[data-bind*="RegAddress"] input', "Москва, ул. Тверская, д. 13", "Адрес регистрации")
    safe_fill(page, 'div[data-bind*="ActualAddress"] .data-container input', "Москва, ул. Тверская, д. 13",
              "Адрес фактического пребывания")
    print("💾 Нажимаем кнопку 'Сохранить'...")

    save_button_clicked = False

    # Вариант 1: Поиск по точному тексту с force=True
    try:
        save_btn = page.get_by_role("button", name="Сохранить", exact=True)
        if save_btn.count() > 0:
            save_btn.scroll_into_view_if_needed()
            save_btn.click(force=True)
            print("✅ Кнопка 'Сохранить' нажата (force click)")
            save_button_clicked = True
    except Exception as e:
        print(f"   Вариант 1 не сработал: {e}")

    print("✅ Вкладка 'Физические лица' (юрлицо) заполнена!")
    return True


def fill_legal_entity_form(page: Page) -> None:
    """Заполняет анкету ЮРИДИЧЕСКОГО лица"""
    print("📋 Начинаем заполнение анкеты ЮРИДИЧЕСКОГО лица...")

    print("\n========== ВКЛАДКА 1: ЕГРЮЛ ==========")
    safe_upload_file(page, '#EgrulCharterFile .select-link', "/Users/new/Documents/устав.jpeg", "Устав")

    print("\n========== ВКЛАДКА 2: ОПРОСНЫЙ ЛИСТ ==========")
    fill_legal_entity_questionnaire_tab(page)

    print("\n========== ВКЛАДКА 3: ФИЗИЧЕСКИЕ ЛИЦА ==========")
    fill_legal_entity_physical_persons_tab(page)

    print("✅ Анкета юрлица полностью заполнена!")


def fill_client_form(page: Page, client_type: str) -> None:
    """Общая функция для заполнения анкеты"""
    if client_type == "individual":
        print("\n========== ВКЛАДКА 1: ЕГРИП ==========")
        fill_egrip_tab(page)
        print("\n========== ВКЛАДКА 2: ОПРОСНЫЙ ЛИСТ ==========")
        fill_questionnaire_tab(page)
        print("\n========== ВКЛАДКА 3: ФИЗИЧЕСКОЕ ЛИЦО ==========")
        fill_physical_person_tab(page)
    elif client_type == "legal_entity":
        fill_legal_entity_form(page)


# ============================================================================
# 🎯 ОСНОВНОЙ ТЕСТ
# ============================================================================

def test_agent_login() -> None:
    p = sync_playwright().start()

    try:
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
        context = browser.contexts[0]
        page = context.pages[-1] if context.pages else context.new_page()

        target_url = "http://dev-03.ru-central1.internal/Account/LogonByDsKey"
        print(f"🌐 Переходим на: {target_url}")
        page.goto(target_url, wait_until="networkidle", timeout=30000)

        if "Home/Index" not in page.url:
            login_agent(page)
        else:
            print("✅ Уже авторизованы")

        print("📋 Переходим в раздел 'Клиенты'...")
        page.get_by_role('link', name='Клиенты').click()
        page.wait_for_load_state("networkidle", timeout=30000)

        print("➕ Нажимаем 'Новый клиент'...")
        page.get_by_role('button', name='Новый клиент').click()
        page.wait_for_selector('text=Введите ИНН Клиента', timeout=10000)
        print("✅ Открыто окно создания клиента")

        inn = get_inn_from_user()
        if not inn:
            print("❌ ИНН не введён!")
            return

        client_type = determine_client_type(inn)
        print(f"✅ ИНН: {inn}, Тип: {client_type}")

        if client_type == "unknown":
            print("❌ ИНН должен содержать 10 или 12 цифр")
            return

        fill_inn_field(page, inn)
        if not click_continue_button(page):
            return

        fill_client_form(page, client_type)

        page.screenshot(path="client_result.png", full_page=True)
        print(f"✅ ТЕСТ ЗАВЕРШЁН\n📄 Финальный URL: {page.url}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        try:
            page.screenshot(path="error_screenshot.png", full_page=True)
        except:
            pass
    finally:
        p.stop()


if __name__ == "__main__":
    test_agent_login()