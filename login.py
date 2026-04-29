from playwright.sync_api import sync_playwright
import time


def test_agent_login():
    p = sync_playwright().start()

    try:
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
        context = browser.contexts[0]
        page = context.pages[-1] if context.pages else context.new_page()

        # 🔴 Переходим на сайт
        target_url = "http://dev-03.ru-central1.internal/Account/LogonByDsKey"
        print(f"🌐 Переходим на: {target_url}")
        page.goto(target_url, wait_until="networkidle", timeout=30000)
        print(f"✅ Загружена: {page.url}")

        # 🔍 Проверяем авторизацию
        is_logged_in = "Home/Index" in page.url
        print(f"🔐 Авторизован: {is_logged_in}")

        # 🔀 Если НЕ авторизованы — выполняем вход
        if not is_logged_in:
            print("🔗 Кликаем 'Вход для агентов'...")
            try:
                page.click('text=Вход для агентов', timeout=10000)
                page.wait_for_load_state("networkidle", timeout=30000)
            except:
                print("⚠️ Не удалось кликнуть")

            print("📝 Заполняем форму...")
            try:
                page.wait_for_selector('#Email', state='visible', timeout=15000)
                page.fill('#Email', 'akinfeev@mail.ru')
                print("✅ Логин заполнен")
            except Exception as e:
                print(f"⚠️ Поле #Email: {e}")

            try:
                page.wait_for_selector('#Password', state='visible', timeout=15000)
                page.fill('#Password', '1q2w!Q@W')
                print("✅ Пароль заполнен")
            except Exception as e:
                print(f"⚠️ Поле #Password: {e}")

            try:
                page.get_by_role('button', name='Войти').click()
                print("✅ Кнопка 'Войти' нажата")
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as e:
                print(f"⚠️ Кнопка входа: {e}")
        else:
            print("✅ Уже авторизованы, пропускаем форму входа")

        # 🔴 ПЕРЕХОДИМ В РАЗДЕЛ "КЛИЕНТЫ"
        print("📋 Переходим в раздел 'Клиенты'...")
        try:
            page.get_by_role('link', name='Клиенты').click()
            page.wait_for_load_state("networkidle", timeout=30000)
            print("✅ Раздел 'Клиенты' открыт")
        except Exception as e:
            print(f"⚠️ Не удалось перейти: {e}")
            page.screenshot(path="debug_clients.png")

        # 🔴 КЛИКАЕМ "НОВЫЙ КЛИЕНТ"
        print("➕ Нажимаем 'Новый клиент'...")
        try:
            page.get_by_role('button', name='Новый клиент').click()
            page.wait_for_selector('text=Введите ИНН Клиента', timeout=10000)
            print("✅ Открыто окно создания клиента")
        except Exception as e:
            print(f"⚠️ Не удалось открыть окно: {e}")
            page.screenshot(path="debug_new_client.png")
            return  # Прерываем, если окно не открылось

        #  ЗАПРОС ИНН ЧЕРЕЗ КОНСОЛЬ (ОБЯЗАТЕЛЬНО ДО ИСПОЛЬЗОВАНИЯ!)
        print("\n" + "=" * 50)
        inn = input("🔢 ВВЕДИТЕ ИНН клиента и нажмите Enter: ").strip()
        print("=" * 50 + "\n")

        if not inn:
            print("❌ ИНН не введён! Прерываем.")
            page.screenshot(path="cancelled.png")
            return

        print(f"✅ Введён ИНН: {inn}")

        # 🔴 ЗАПОЛНЯЕМ ПОЛЕ ИНН
        print("🔢 Заполняем поле ИНН...")

        try:
            # 🔍 Ищем поле ИНН ТОЛЬКО внутри модального окна #newClientModal
            # Это решает проблему "strict mode violation: resolved to 2 elements"
            inn_field = page.locator('#newClientModal input.controls.mywidth')
            inn_field.fill(inn)
            print("✅ ИНН заполнен")

            # 🔴 🔴 🔴 ВАЖНО: Снимаем фокус с поля, чтобы сработала валидация
            print("⏳ Снимаем фокус с поля (нажимаем Tab)...")
            page.keyboard.press('Tab')
            time.sleep(1)  # Даём время на валидацию ИНН
            print("✅ Фокус снят, валидация выполнена")

        except Exception as e:
            print(f"⚠️ Ошибка заполнения ИНН: {e}")

            # Пробуем альтернативные селекторы, если основной не сработал
            try:
                inn_field = page.locator('#newClientModal [data-bind*="ClientInn"]').last
                inn_field.fill(inn)
                page.keyboard.press('Tab')
                time.sleep(1)
                print("✅ ИНН заполнен (альтернативный селектор)")
            except:
                print("❌ Не удалось заполнить ИНН")
                page.screenshot(path="error_inn_field.png")
                return

        # 🔴 ЖДЁМ АКТИВАЦИИ КНОПКИ "ПРОДОЛЖИТЬ"
        print("⏳ Ждём активации кнопки 'Продолжить'...")
        try:
            # Ищем кнопку ТОЛЬКО внутри модального окна
            continue_btn = page.locator('#newClientModal button.btn-primary')
            continue_btn.wait_for(state='visible', timeout=10000)

            # Проверяем, разблокировалась ли кнопка
            if continue_btn.is_disabled():
                print("⚠️ Кнопка всё ещё заблокирована")
                # Пробуем ещё раз снять фокус кликом в заголовок
                try:
                    page.click('#newClientModal .modal-header', timeout=5000)
                    time.sleep(1)
                    if not continue_btn.is_disabled():
                        print("✅ Кнопка разблокировалась после клика")
                except:
                    pass

                if continue_btn.is_disabled():
                    print("❌ Кнопка осталась заблокированной (проверьте ИНН)")
                    page.screenshot(path="button_disabled.png")
                    return
            else:
                print("✅ Кнопка активна, нажимаем...")
                continue_btn.click(timeout=10000)
                print("✅ 'Продолжить' нажата")

                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(2)

        except Exception as e:
            print(f"⚠️ Ошибка с кнопкой 'Продолжить': {e}")
            page.screenshot(path="error_continue.png")

        # Финальный скриншот
        page.screenshot(path="client_result.png", full_page=True)
        print(f"✅ ТЕСТ ЗАВЕРШЁН")
        print(f"📄 Финальный URL: {page.url}")

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