Выбираем ветку master
2. Создание виртуального окружения
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка базы данных
bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
5. Запуск сервера
bash
python manage.py runserver
Приложение будет доступно по адресу: http://127.0.0.1:8000/
