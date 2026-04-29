print("☑️ 9. Выбираем переключатель 'Нет' (счет в другом банке)...")

# Самый надёжный селектор для вашей разметки
radio_no_selector = 'input[type="radio"][name="haveLocalBankAccountsOptions"][value="1"]'

# Кликаем
page.check(radio_no_selector)

# Верифицируем, что выбрана правильная кнопка
assert page.is_checked(radio_no_selector), "Радио-кнопка 'Да' не выбрана"

# Проверяем, что соседняя 'ДА' не выбрана
radio_new_selector = 'input[type="radio"][name="haveLocalBankAccountsOptions"][value="0"]'
assert not page.is_checked(radio_new_selector), "Радио-кнопка 'Да' ошибочно выбрана"

print("✅ Переключатель 'Нет' выбран (подтверждено)")


print("☑️ 10. Выбираем переключатель 'Нет' (счета в локальных банках)...")
page.check('input[name="haveLocalBankAccountsOptions"][value="1"]')
assert page.is_checked('input[name="haveLocalBankAccountsOptions"][value="1"]')
print("✅ Переключатель 'Нет' выбран")
