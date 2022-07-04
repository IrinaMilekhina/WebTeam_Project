import os
import logging

from ProductPlatform.settings import DEBUG

FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'change_order_status.logs')
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
if DEBUG:
    LOG_FILE.setLevel(logging.DEBUG)
else:
    LOG_FILE.setLevel(logging.INFO)
LOG_FILE.setFormatter(FORMATTER)
logger = logging.getLogger(__name__)
logger.addHandler(LOG_FILE)