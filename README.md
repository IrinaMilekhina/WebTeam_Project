# WebTeam_Project

# Командная разработка по методологии Agile:Scrum

# Проект "Product platform"
Это приложение предназначено для реализации продовольственных заказов. В котором кафе, рестораны выступают в роли заказчика и размещают на выполнение заказы на приобретение продовольственных товаров, а поставщики в свою очередь регистрируются на платформе для отклика на созданные заказы и просматривают информацию о конкурентах и коллегах.

## Демо
Посетите http://176.210.101.126:5072 для демонстрации в реальном времени. 

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
python manage.py makemigrations #filling database
python manage.py migrate # run first migration
python manage.py loaddata main_fixtures.json
python manage.py runserver # run the server
```
В браузере ввести адрес http://127.0.0.1:8000 и откроется проект.


## License
© 2022 HORECA_MALL
