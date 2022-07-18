import threading
import time
from datetime import datetime, timedelta

import schedule as schedule

from ProductPlatform.script.log_change_status_order import logger
from ProductPlatform.settings import TIME_START_CHECK_ORDER_STATUS
from orders.models import Order, StatusResponse


def check_order_status():
    """Проверка активных заказов: если дата окончания заказа
     end_time истекла, то
    перевод Заказа в статус Not Active"""
    orders = Order.objects.filter(status='Active')
    for order in orders:
        if datetime.date(order.end_time) < datetime.today().date():
            logger.warning(f'Change status: {order}')
            order.status = 'Not Active'
            order.save()
    logger.info(datetime.now(), "Check_order_status_DONE...")


def start_planner():
    """Запуск планировщика"""
    try:
        for st_time in TIME_START_CHECK_ORDER_STATUS:
            tz = int(datetime.now().astimezone().strftime("%z")[:3])
            delta_tz = tz - 3
            real_hour = int(st_time.split(':')[0]) + delta_tz
            if real_hour > 23:
                real_hour = real_hour-24
            if real_hour < 10:
                real_hour = f'0{real_hour}'
            start_time = f"{real_hour}:{st_time.split(':')[1]}"
            schedule.every().day.at(start_time).do(check_order_status)  # проверка ордеров по времени CHECK_TIME
        # schedule.every(1).minutes.do(check_order_status)  # для теста проверка через 1 минуту
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception:
        logger.error('error start planner check order status')


def start_thread_check_order_status():
    """Запуск потока проверки статусов Заказов"""
    logger.warning('start thread check order...')
    my_thread = threading.Thread(target=start_planner)
    my_thread.daemon = True
    my_thread.start()
