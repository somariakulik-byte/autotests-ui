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
    """Заполняет вкладку 'Физические лица' для юрлица (поддерживает несколько блоков с разными данными)"""
    print("📋 Начинаем заполнение вкладки 'Физические лица' (юрлицо)...")
    if not switch_to_tab(page, '.tab[content="tab-content-physicalpersons"]', "Физические лица"):
        return False

    # 📋 Данные для каждого блока (индекс блока -> данные)
    persons_data = {
        0: {  # Блок 1
            'series': "4515",
            'number': "152452",
            'dept_code': "515-215",
            'issue_date': (2026, 3, 1),  # 01.04.2026
            'issued_by': "ОВД Мичуринского района",
            'birth_date': (2012, 3, 1),  # 01.04.2012
            'birth_place': "Москва",
            'reg_address': "Москва, ул. Тверская, д. 13",
            'actual_address': "Москва, ул. Тверская, д. 13",
            'scan_required': True  # Скан нужен только для первого блока
        },
        1: {  # Блок 2
            'series': "7421",
            'number': "987654",
            'dept_code': "770-001",
            'issue_date': (2025, 6, 15),  # 15.07.2025
            'issued_by': "ОМВД России по г. Москве",
            'birth_date': (1985, 2, 20),  # 20.03.1985
            'birth_place': "Санкт-Петербург",
            'reg_address': "Санкт-Петербург, Невский пр-т, д. 25",
            'actual_address': "Санкт-Петербург, Невский пр-т, д. 25",
            'scan_required': False
        },
        2: {  # Блок 3
            'series': "9632",
            'number': "456123",
            'dept_code': "550-987",
            'issue_date': (2024, 9, 10),  # 10.10.2024
            'issued_by': "УФМС России по Московской области",
            'birth_date': (1990, 7, 5),  # 05.08.1990
            'birth_place': "Екатеринбург",
            'reg_address': "Екатеринбург, ул. Ленина, д. 50",
            'actual_address': "Екатеринбург, ул. Ленина, д. 50",
            'scan_required': False
        },
        3: {  # Блок 4
            'series': "1548",
            'number': "789321",
            'dept_code': "340-567",
            'issue_date': (2023, 12, 25),  # 25.01.2024
            'issued_by': "ГУ МВД России по Нижегородской области",
            'birth_date': (1975, 11, 8),  # 08.12.1975
            'birth_place': "Нижний Новгород",
            'reg_address': "Нижний Новгород, ул. Большая Покровская, д. 10",
            'actual_address': "Нижний Новгород, ул. Большая Покровская, д. 10",
            'scan_required': False
        },
        4: {  # Блок 5
            'series': "3579",
            'number': "246813",
            'dept_code': "890-432",
            'issue_date': (2025, 1, 20),  # 20.02.2025
            'issued_by': "Отдел полиции №1 г. Казань",
            'birth_date': (1988, 4, 18),  # 18.05.1988
            'birth_place': "Казань",
            'reg_address': "Казань, ул. Баумана, д. 15",
            'actual_address': "Казань, ул. Баумана, д. 15",
            'scan_required': False
        },
    }

    # Находим все блоки
    blocks = page.locator('section[style*="margin-bottom: 15px"]').all()

    if not blocks:
        print("⚠️ Блоки не найдены")
        return False

    print(f"   Найдено блоков: {len(blocks)}")

    # Перебираем все блоки
    for block_index in range(len(blocks)):
        print(f"\n--- Заполнение блока {block_index + 1} из {len(blocks)} ---")

        # Получаем данные для текущего блока (если нет, используем данные первого блока)
        data = persons_data.get(block_index, persons_data[0])

        # Заново находим кнопки "Редактировать"
        edit_buttons = page.locator('button:has-text("Редактировать")').all()
        if block_index >= len(edit_buttons):
            print(f"   Блок {block_index + 1} больше не доступен")
            break

        edit_buttons[block_index].scroll_into_view_if_needed()
        edit_buttons[block_index].click()
        print(f"   ✅ Кнопка 'Редактировать' нажата для блока {block_index + 1}")
        page.wait_for_timeout(2000)

        # Загрузка скана паспорта (только если требуется)
        if data.get('scan_required', False):
            print("   📎 Загружаем скан паспорта...")
            try:
                scan_button = page.locator('#DocumentScan-1 .select-link')
                if scan_button.count() > 0 and scan_button.is_visible():
                    with page.expect_file_chooser() as fc_info:
                        scan_button.click()
                    fc_info.value.set_files("/Users/new/Documents/паспорт.jpg")
                    print(f"   ✅ Блок {block_index + 1}: Скан паспорта загружен")
                else:
                    print(f"   ⚠️ Блок {block_index + 1}: Кнопка загрузки скана не найдена")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Ошибка загрузки скана: {e}")
        else:
            print(f"   ℹ️ Блок {block_index + 1}: Загрузка скана не требуется")

        # Серия
        series_filled = False
        for suffix in [block_index, block_index - 1 if block_index > 0 else 0]:
            series_selector = f'#Series-{suffix}'
            series_field = page.locator(series_selector)
            if series_field.count() > 0 and series_field.is_visible() and not series_field.is_disabled():
                series_field.fill(data['series'])
                print(f"   ✅ Блок {block_index + 1}: Серия '{data['series']}' заполнена")
                series_filled = True
                break
        if not series_filled:
            try:
                series_field = page.locator('[data-bind*="Series"] input:visible:not([disabled])').first
                series_field.fill(data['series'])
                print(f"   ✅ Блок {block_index + 1}: Серия '{data['series']}' заполнена")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Не удалось заполнить Серию: {e}")

        # Номер
        number_filled = False
        for suffix in [block_index, block_index - 1 if block_index > 0 else 0]:
            number_selector = f'#Number-{suffix}'
            number_field = page.locator(number_selector)
            if number_field.count() > 0 and number_field.is_visible() and not number_field.is_disabled():
                number_field.fill(data['number'])
                print(f"   ✅ Блок {block_index + 1}: Номер '{data['number']}' заполнен")
                number_filled = True
                break
        if not number_filled:
            try:
                number_field = page.locator('[data-bind*="Number"] input:visible:not([disabled])').first
                number_field.fill(data['number'])
                print(f"   ✅ Блок {block_index + 1}: Номер '{data['number']}' заполнен")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Не удалось заполнить Номер: {e}")

        # Код подразделения
        dept_filled = False
        for suffix in [block_index, block_index - 1 if block_index > 0 else 0]:
            dept_selector = f'#DepartmentCode-{suffix}'
            dept_field = page.locator(dept_selector)
            if dept_field.count() > 0 and dept_field.is_visible() and not dept_field.is_disabled():
                dept_field.fill(data['dept_code'])
                print(f"   ✅ Блок {block_index + 1}: Код подразделения '{data['dept_code']}' заполнен")
                dept_filled = True
                break
        if not dept_filled:
            try:
                dept_field = page.locator('[data-bind*="DepartmentCode"] input:visible:not([disabled])').first
                dept_field.fill(data['dept_code'])
                print(f"   ✅ Блок {block_index + 1}: Код подразделения '{data['dept_code']}' заполнен")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Не удалось заполнить Код подразделения: {e}")

        # Дата выдачи
        date_filled = False
        try:
            date_fields = page.locator('[id*="IssueDateElement"]').all()
            for df in date_fields:
                if df.is_visible() and not df.is_disabled():
                    year, month, day = data['issue_date']
                    date_str = f"{day:02d}.{month + 1:02d}.{year}"
                    df.click()
                    df.clear()
                    df.fill(date_str)
                    print(f"   ✅ Блок {block_index + 1}: Дата выдачи '{date_str}' заполнена")
                    date_filled = True
                    break
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Ошибка при заполнении даты выдачи: {e}")

        if not date_filled:
            try:
                year, month, day = data['issue_date']
                set_datepicker(page, '#IssueDateElement-0', f"Дата выдачи (блок {block_index + 1})", year, month, day)
                print(f"   ✅ Блок {block_index + 1}: Дата выдачи заполнена через datepicker")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Не удалось заполнить Дату выдачи: {e}")

        # Выдан кем
        try:
            issued_by_field = page.locator('[data-bind*="Issuer"] input:visible:not([disabled])').first
            if issued_by_field.count() > 0:
                issued_by_field.fill(data['issued_by'])
                print(f"   ✅ Блок {block_index + 1}: 'Выдан кем' - '{data['issued_by']}'")
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: 'Выдан кем' не заполнено: {e}")

        # Дата рождения
        birth_date_filled = False
        try:
            birth_date_fields = page.locator('[id*="BirthDateElement"]').all()
            for bf in birth_date_fields:
                if bf.is_visible() and not bf.is_disabled():
                    year, month, day = data['birth_date']
                    date_str = f"{day:02d}.{month + 1:02d}.{year}"
                    bf.click()
                    bf.clear()
                    bf.fill(date_str)
                    print(f"   ✅ Блок {block_index + 1}: Дата рождения '{date_str}' заполнена")
                    birth_date_filled = True
                    break
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Ошибка при заполнении даты рождения: {e}")

        if not birth_date_filled:
            try:
                year, month, day = data['birth_date']
                set_datepicker(page, '#BirthDateElement-0', f"Дата рождения (блок {block_index + 1})", year, month, day)
                print(f"   ✅ Блок {block_index + 1}: Дата рождения заполнена через datepicker")
            except Exception as e:
                print(f"   ⚠️ Блок {block_index + 1}: Не удалось заполнить Дату рождения: {e}")

        # Место рождения
        try:
            birth_place_field = page.locator('[data-bind*="BirthPlace"] input:visible:not([disabled])').first
            if birth_place_field.count() > 0:
                birth_place_field.fill(data['birth_place'])
                print(f"   ✅ Блок {block_index + 1}: Место рождения - '{data['birth_place']}'")
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Место рождения не заполнено: {e}")

        # Адрес регистрации
        try:
            reg_address_field = page.locator('[data-bind*="RegAddress"] input:visible:not([disabled])').first
            if reg_address_field.count() > 0:
                reg_address_field.fill(data['reg_address'])
                print(f"   ✅ Блок {block_index + 1}: Адрес регистрации - '{data['reg_address']}'")
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Адрес регистрации не заполнен: {e}")

        # Адрес фактического пребывания
        try:
            actual_address_field = page.locator('[data-bind*="ActualAddress"] input:visible:not([disabled])').first
            if actual_address_field.count() > 0:
                actual_address_field.fill(data['actual_address'])
                print(f"   ✅ Блок {block_index + 1}: Адрес фактического пребывания - '{data['actual_address']}'")
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Адрес фактического пребывания не заполнен: {e}")

        # Сохраняем блок
        print(f"   💾 Сохраняем блок {block_index + 1}...")
        try:
            save_btn = page.get_by_role("button", name="Сохранить", exact=True)
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                print(f"   ✅ Блок {block_index + 1}: Сохранен")
            else:
                save_btn = page.locator('button:has-text("Сохранить")').first
                if save_btn.count() > 0:
                    save_btn.click(force=True)
                    print(f"   ✅ Блок {block_index + 1}: Сохранен (force click)")
        except Exception as e:
            print(f"   ⚠️ Блок {block_index + 1}: Не удалось сохранить: {e}")

        page.wait_for_timeout(2000)

    print("\n✅ Вкладка 'Физические лица' (юрлицо) полностью заполнена!")
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