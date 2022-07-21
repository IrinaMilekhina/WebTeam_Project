# WebTeam_Project

# Командная разработка по методологии Agile:Scrum

# Проект "Product platform"
Это приложение предназначено для реализации продовольственных заказов. В которой кафе, рестораны выступают в роли заказчика и размещают на выполнение заказы на приобретение продовольственных товаров, а поставщики в свою очередь регистрируются на платформе для отклика на созданные заказы и просматривают информацию о конкурентах и коллегах.

## Применение
Лучше всего устанавливать проекты Python в виртуальной среде. После того, как вы настроили VE, клонируйте этот проект

```bash
git clone https://github.com/IrinaMilekhina/WebTeam_Project.git
```
Потом

```bash
cd ProductPlatform
```
Запуск приложения

```python
pip install -r requirements.txt #install required packages
python manage.py loaddata main_fixtures.json
python manange.py migrate # run first migration
python manange.py runserver # run the server
```
В браузере ввести адрес http://172.0.0.1:8000 и откроется проект.

## Авторизация администратора
Когда вы запускаете миграцию, создается суперпользователь.
```bash
username: ADMIN
password: ADMIN
```

## Авторизация Заказчика

```bash
username: user1
password: 1q1w1e1r

username: user2
password: 2q2w2e2r

username: user3
password: 3q3w3e3r
```

## Авторизация Поставщика

```bash
username: user4
password: 4q4w4e4r

username: user5
password: 5q5w5e5r
```

## License
© 2022 HORECA_MALL
