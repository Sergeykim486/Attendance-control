import csv
from datetime import datetime
import os
from Classes.db import Database
import threading
import time
import shutil
from colorama import Fore, Style, init
init(autoreset=True)
current_date_path = ''
curdate = datetime.now().strftime('%Y-%m-%d')
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
    create_backup(current_date_path)

    rows.append(data)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

# Функция для проверки смены даты и создания нового файла при смене месяца
def check_date_change():
    global curdate
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d') + '.csv'
    if current_date == curdate:
        result = 0
    else:
        result = 1
    return result

# Функция для проверки смены даты в фоновом потоке
def date_check_thread():
    global current_date_path
    while True:
        time.sleep(15)  # Проверяем каждую минуту
        # create_backup(current_date_path)
        if check_date_change() == 1:
            db_filename = 'Classes/Database/db.db'
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d') + '.csv'
            day_folder = 'Day'
            month_folder = os.path.join(day_folder, now.strftime('%Y-%m'))
            if not os.path.exists(day_folder):
                os.mkdir(day_folder)
            if not os.path.exists(month_folder):
                os.mkdir(month_folder)
            current_date_path = os.path.join(month_folder, current_date)
            db = Database(db_filename)
            users_data = db.select_table('Users')  # Здесь предполагается, что у вас есть таблица "Users" в базе данных
            departments_data = db.select_table('Departments')  # Здесь предполагается, что у вас есть таблица "Departments" в базе данных
            department_names = {department[0]: department[1] for department in departments_data}
            
            try:
                with open(current_date_path, mode='r'):
                    with open(current_date_path, mode='r') as file:
                        reader = csv.reader(file, delimiter=';')
                        etalone = list(reader)
                        write_to_csv(current_date_path, users_data, etalone, department_names)
            except FileNotFoundError:
                etalone = {}
                write_to_csv(current_date_path, users_data, etalone, department_names)

def write_to_csv(current_date_path, users_data, etalone, department_names):
    # Заполняем CSV данными о пользователях
    with open(current_date_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['#', 'Имя пользователя', 'id пользователя', 'Подразделение', 'Время прихода', 'Время ухода'])
        for index, user in enumerate(users_data, start=1):
            tin = '--:--'
            tof = '--:--'
            try:
                for line in etalone[1:]:
                    id = int(line[2])
                    userid = int(user[0])
                    if id == userid:
                        tin = line[4]
                        tof = line[5]
            except:
                pass
            user_id, user_name, department_id = user[0], user[1], user[2]
            department_name = department_names.get(department_id, 'Unknown Department')
            writer.writerow([index, user_name, user_id, department_name, tin, tof])
    create_backup(current_date_path)

# Функция для создания бэкапа основного файла
def create_backup(filename):
    try:
        backup_filename = filename.replace('.csv', '_backup.csv')
        shutil.copyfile(filename, backup_filename)
    except Exception as e:
        print(f"Error creating backup: {e}")

# Функция для восстановления из бэкапа
def restore_from_backup(filename):
    try:
        backup_filename = filename.replace('.csv', '_backup.csv')
        shutil.copyfile(backup_filename, filename)
    except Exception as e:
        print(f"Error restoring from backup: {e}")

# Основная часть программы
if __name__ == '__main__':
    
    try:
    
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
# Проверяем существование файла CSV текущего дня
        try:
            with open(current_date_path, mode='r'):
                with open(current_date_path, mode='r') as file:
                    reader = csv.reader(file, delimiter=';')
                    etalone = list(reader)
                    if etalone != {}:
                    #     write_to_csv(current_date_path, users_data, etalone, department_names)
                    # else:
                        try:
                            restore_from_backup(current_date_path)
                        except (FileNotFoundError, csv.Error) as e:
                            # Если не удалось восстановить из бэкапа, создаем новый файл
                            print(f'Error: {e}. Creating a new file...')
                            with open(current_date_path, mode='w', newline='') as file:
                                writer = csv.writer(file, delimiter=';')
                                writer.writerow(['#', 'Имя пользователя', 'id пользователя', 'Подразделение', 'Время прихода', 'Время ухода'])
                            create_backup(current_date_path)
                        
        except (FileNotFoundError, csv.Error) as e:
            # Если файл отсутствует или поврежден, восстанавливаем из резервной копии
            # print(f'Error: {e}. Restoring from backup...')
            restore_from_backup(current_date_path)
            try:
                with open(current_date_path, mode='r') as file:
                    reader = csv.reader(file, delimiter=';')
                    etalone = list(reader)
                    write_to_csv(current_date_path, users_data, etalone, department_names)
                    print(f'Restored from backup: {current_date_path}')
            except (FileNotFoundError, csv.Error) as e:
                # Если не удалось восстановить из бэкапа, создаем новый файл
                print(f'Error: {e}. Creating a new file...')
                with open(current_date_path, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(['#', 'Имя пользователя', 'id пользователя', 'Подразделение', 'Время прихода', 'Время ухода'])
                create_backup(current_date_path)
                # print(f'New file created: {current_date_path}')

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
    
    except:
        pass