import threading
import time
from datetime import datetime, timedelta

import schedule as schedule

from orders.models import Order, StatusResponse

CHECK_TIME = "00:00"  # запуск скрипта, время по москве

def check_order_status():
    """Проверка активных заказов: если дата окончания заказа
     end_time истекла или с момента
    утверждения отклика прошло 3 дня, то
    перевод Заказа в статус Not Active"""
    orders = Order.objects.filter(status='Active')
    status_response = StatusResponse.objects.filter(status='Approved')
    for order in orders:
        order_responses = status_response.filter(response_order__order__id=order.id).first()
        if datetime.date(order.end_time) < datetime.today().date() \
                or (order_responses and datetime.date(order_responses.time_status) + timedelta(
            days=3) < datetime.today().date()):
            print(f'Change status: {order}')
            order.status = 'Not Active'
            order.save()
    print(datetime.now(), "Check_order_status_DONE...")


def start_planner():
    """Запуск планировщика"""
    tz = int(datetime.now().astimezone().strftime("%z")[:3])
    delta_tz = tz - 3
    real_hour = int(CHECK_TIME.split(':')[0]) + delta_tz
    if real_hour < 10:
        real_hour = f'0{real_hour}'
    start_time = f"{real_hour}:{CHECK_TIME.split(':')[1]}"
    schedule.every().day.at(start_time).do(check_order_status)  # проверка ордеров по времени CHECK_TIME
    # schedule.every(1).minutes.do(check_order_status)  # для теста проверка через 1 минуту
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_thread_check_order_status():
    """Запуск потока проверки статусов Заказов"""
    print('start thread check order...')
    my_thread = threading.Thread(target=start_planner)
    my_thread.start()
