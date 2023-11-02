import csv
from datetime import datetime
import os
from Classes.db import Database
import threading
import time
from colorama import Fore, Style, init
init(autoreset=True)
import schedule  # Импорт модуля для управления расписанием

# Функция для создания или обновления CSV файла
def create_or_update_csv(filename, data):
    try:
        with open(filename, mode='r') as file:
            # Файл уже существует, читаем его
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
    except FileNotFoundError:
        # Файл не существует, создаем новый с заголовком
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['№', 'Имя пользователя', 'id пользователя', 'Подразделение', 'Время прихода', 'Время ухода'])
        rows = []

    # Обновляем данные в файле
    for i, row in enumerate(rows):
        if row[2] == data[2]:  # Пользователь уже существует
            return

    rows.append(data)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

# Функция для проверки смены даты и создания нового файла при смене месяца
def check_date_change():
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d') + '.csv'
    current_month = now.strftime('%Y-%m')

    return current_date, current_month

# Функция для проверки смены даты в фоновом потоке
def date_check_thread():
    current_date, current_month = check_date_change()

    while True:
        time.sleep(60)  # Проверяем каждую минуту
        new_date, new_month = check_date_change()

        if current_date != new_date:
            # Дата сменилась, выполнить необходимые действия при смене даты
            print("Дата сменилась. Выполнение действий при смене даты...")
            current_date = new_date

        if current_month != new_month:
            # Месяц сменился, выполнить необходимые действия при смене месяца
            print("Месяц сменился. Выполнение действий при смене месяца...")
            current_month = new_month

# Функция для проверки и добавления новых пользователей в CSV файл
def check_and_add_new_users(current_date_path, users_data):
    # Открываем CSV файл для чтения
    with open(current_date_path, mode='r') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    # Получим список всех id пользователей, уже находящихся в файле
    existing_user_ids = [row[2] for row in rows]

    # Проверяем каждого пользователя из базы данных
    for user in users_data:
        user_id, user_name, department_id = user[0], user[1], user[2]
        department_name = department_names.get(department_id, 'Unknown Department')

        # Если пользователь еще не добавлен в файл, добавляем его
        if user_id not in existing_user_ids:
            # Генерируем новую строку для пользователя
            new_user_row = [len(existing_user_ids) + 1, user_name, user_id, department_name, '--:--', '--:--']
            rows.append(new_user_row)

    # Записываем обновленные данные обратно в CSV файл
    with open(current_date_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

# Функция для проверки и добавления новых пользователей в CSV файл
def check_and_add_new_users(current_date_path, users_data):
    # Открываем CSV файл для чтения
    with open(current_date_path, mode='r') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    # Получим список всех id пользователей, уже находящихся в файле
    existing_user_ids = [row[2] for row in rows]

    # Проверяем каждого пользователя из базы данных
    for user in users_data:
        user_id, user_name, department_id = user[0], user[1], user[2]
        department_name = department_names.get(department_id, 'Unknown Department')

        # Если пользователь еще не добавлен в файл, добавляем его
        if user_id not in existing_user_ids:
            # Генерируем новую строку для пользователя
            new_user_row = [len(existing_user_ids) + 1, user_name, user_id, department_name, '--:--', '--:--']
            rows.append(new_user_row)

    # Записываем обновленные данные обратно в CSV файл
    with open(current_date_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

# Функция для проверки смены даты и создания нового файла при смене месяца
def check_date_change():
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d') + '.csv'
    current_month = now.strftime('%Y-%m')

    return current_date, current_month

# Функция для выполнения проверки и добавления новых пользователей каждые 15 секунд
def schedule_check_and_add_users():
    current_date_path, users_data = None, None
    while True:
        new_date, new_month = check_date_change()

        if current_date_path != new_date:
            # Дата сменилась, выполнить необходимые действия при смене даты
            current_date_path = new_date
            users_data = db.select_table('Users')
        
        if current_month != new_month:
            # Месяц сменился, выполнить необходимые действия при смене месяца
            current_month = new_month
        
        if current_date_path and users_data:
            check_and_add_new_users(current_date_path, users_data)
        
        time.sleep(15)  # Проверяем каждые 15 секунд

# Добавляем задачу для выполнения проверки и добавления новых пользователей каждые 15 секунд
schedule.every(15).seconds.do(schedule_check_and_add_users)

# Основная часть программы
if __name__ == '__main__':
    
    # Имя файла базы данных
    db_filename = 'Classes/Database/db.db'

    # Получаем текущую дату и время
    now = datetime.now()

    # Имя файла CSV для текущей даты (в формате "год-месяц-день.csv")
    current_date = now.strftime('%Y-%m-%d') + '.csv'

    # Папка для файлов текущего дня
    day_folder = 'Day'

    # Папка для файлов текущего месяца
    month_folder = os.path.join(day_folder, now.strftime('%Y-%m'))

    # Создаем каталоги, если они не существуют
    if not os.path.exists(day_folder):
        os.mkdir(day_folder)
    if not os.path.exists(month_folder):
        os.mkdir(month_folder)

    # Полный путь к файлу CSV для текущей даты
    current_date_path = os.path.join(month_folder, current_date)

    # Инициализируем базу данных
    db = Database(db_filename)

    # Получаем данные о пользователях из базы данных
    users_data = db.select_table('Users')  # Здесь предполагается, что у вас есть таблица "Users" в базе данных
    departments_data = db.select_table('Departments')  # Здесь предполагается, что у вас есть таблица "Departments" в базе данных

    # Словарь для быстрого доступа к названиям подразделений по id
    department_names = {department[0]: department[1] for department in departments_data}

    # Проверяем существование файла CSV текущего дня
    try:
        with open(current_date_path, mode='r'):
            # Файл существует, ничего не делаем
            pass
    except FileNotFoundError:
        # Файл не существует, создаем новый с заголовком
        with open(current_date_path, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['#', 'Имя пользователя', 'id пользователя', 'Подразделение', 'Время прихода', 'Время ухода'])

        # Заполняем CSV данными о пользователях
        with open(current_date_path, mode='a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for index, user in enumerate(users_data, start=1):
                user_id, user_name, department_id = user[0], user[1], user[2]
                department_name = department_names.get(department_id, 'Unknown Department')
                writer.writerow([index, user_name, user_id, department_name, '--:--', '--:--'])

        print(f'Файл CSV для {current_date} создан и заполнен данными о пользователях.')

    # Создаем и запускаем поток для проверки смены даты
    date_check_thread = threading.Thread(target=date_check_thread)
    date_check_thread.daemon = True  # Поток будет работать в фоновом режиме
    date_check_thread.start()

    # Режим ожидания ввода id пользователя
    while True:
        os.system('cls')
        print(Fore.BLUE + '╔═════════════════════════════════════════════╗')
        print(Fore.BLUE + '║ ДОБРО ПОЖАЛОВАТЬ                            ║')
        print(Fore.BLUE + '╟─────────────────────────────────────────────╢')
        print(Fore.BLUE + '║ Пожалуйста отсканируйте свою карту          ║')
        print(Fore.BLUE + '╚═════════════════════════════════════════════╝')
        print(Style.RESET_ALL)
        user_id = input('Ожидаю сканирования... ')

        if user_id.lower() == 'exit':
            break
        elif user_id.lower() == 'ins':
            uid = input('Отсканируйте карту нового пользователя... -> ')
            uname = input('Введите с клавиатуры имя нового пользователя... -> ')
            udep = input('Выберите отдел нового пользователя:\n1	Администрация\n2	Отдел продаж\n3	Инновации\n4	Логистика\n5	Лаборатория\n6	Экспресс картридж\n7	Бухгалтерия\n8	IT отдел\n-> ')
            dep = db.get_record_by_id('Departments', udep)
            finish = 0
            while finish != 1:
                print(f'id пользователя: {uid}\nИмя пользователя: {uname}\nПодразделение{dep}\n')
                answer = input('Подтвердите введенную информацию\nY - Да / N - Нет:\n-> ')                
                if answer == 'y' or answer == 'Y':
                    db.insert_record('Users',[uid, uname, udep])
                    print(f'Пользователь "{uname}" успешно сохранен...')
                    finish = 1
                elif answer == 'n' or answer == 'N':
                    print('Операция отменена...')
                    finish = 1
                else:
                    print('Вы не подтвердили введенную информацию')
                    finish = 0
            
        else:

            # Поиск пользователя в файле CSV
            with open(current_date_path, mode='r') as file:
                reader = csv.reader(file, delimiter=';')
                rows = list(reader)

            user_info = None
            for row in rows:
                if row[2] == user_id:
                    user_info = row
                    break

            if user_info:
                os.system('cls')
                current_time = datetime.now().strftime('%H:%M')
                if user_info[4] == '--:--':
                    user_info[4] = current_time
                    print(Fore.GREEN + '═════════════════════════════════════════════════════════════════')
                    print(Fore.GREEN + f'    Здравствуйте {user_info[1]}:\n    Время: {current_time}\n    ХОРОШЕГО РАБОЧЕГО ДНЯ!')
                    print(Fore.GREEN + '═════════════════════════════════════════════════════════════════')
                    print(Style.RESET_ALL)
                else:
                    user_info[5] = current_time
                    print(Fore.GREEN + '═════════════════════════════════════════════════════════════════')
                    print(Fore.GREEN + f'    Досвидания {user_info[1]}:\n    Время ухода: {current_time}\n    ПРИЯТНОГО ОТДЫХА!')
                    print(Fore.GREEN + '═════════════════════════════════════════════════════════════════')
                    print(Style.RESET_ALL)

                with open(current_date_path, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerows(rows)
                # print(f'Время ухода для пользователя {user_info[1]} зарегистрировано: {current_time}')
            else:
                os.system('cls')
                print(Fore.RED + '═════════════════════════════════════════════════════════════════')
                print(Fore.RED + '    Пользователь с таким id не найден.')
                print(Fore.RED + '═════════════════════════════════════════════════════════════════')
                print(Style.RESET_ALL)
            time.sleep(3)

    # Создаем и запускаем поток для проверки смены даты
    date_check_thread = threading.Thread(target=date_check_thread)
    date_check_thread.daemon = True  # Поток будет работать в фоновом режиме
    date_check_thread.start()

    # Добавляем бесконечный цикл, чтобы расписание продолжало работать
    while True:
        schedule.run_pending()
        time.sleep(1)