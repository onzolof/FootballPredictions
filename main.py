import logging
from datetime import datetime

from selenium.webdriver.chrome import webdriver


def run():
    today = datetime.date.today().day
    logger = _get_logger()
    # test
    driver = _get_driver()
    driver.close()


def _get_logger():
    logging.basicConfig(filename="advent_bot.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger: logging.Logger = logging.getLogger('transfermarkt_scraper')
    return logger


def _get_driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    driver.maximize_window()
    return driver


if __name__ == '__main__':
    run()
