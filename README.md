# Homework Bot

----------------------------------------
## Описание

Телеграм-бот, сообщающий об изменениях статуса проверки домашнего задания 
в Я.Практикум.

----------------------------------------
## Используемые технологии

 - Python 3.7
 - python-telegram-bot
 
----------------------------------------
## Установка

1. Клонируйте репозиторий
```bash
git clone https://github.com/lmashik/homework_bot.git
```

2. Создайте и активируйте виртуальное окружение
```bash
python3.7 -m venv venv
```

* Если у вас Linux/macOS

    ```bash
    source venv/bin/activate
    ```

* Если у вас windows

    ```bash
    source venv/scripts/activate
    ```

3. Обновите pip до последней версии
```bash
python3 -m pip install --upgrade pip
```

4. Установите зависимости из файла requirements.txt
```bash
pip install -r requirements.txt
```

----------------------------------------
## Запуск

В директории проекта создайте файл .env и заполните его данными по образцу 
.env.example

Затем выполните
```bash
python3 homework.py
```

Бот запущен и будет сообщать вам обо всех изменениях статуса проверки вашей 
домашней работы.

----------------------------------------
## Автор проекта

Лапикова Мария Дмитриевна  
mashik_p@mail.ru
