import csv
import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

show_browser_ui = False
leagues = [
    'https://www.transfermarkt.ch/super-league/startseite/wettbewerb/C1',
    # 'https://www.transfermarkt.ch/bundesliga/startseite/wettbewerb/L1',
]


def run():
    logger = get_logger()
    driver = get_driver()
    do_scraping(driver, logger)
    driver.close()


def scrape_player(driver, player_link):
    player = dict()
    driver.get(player_link)
    no_and_name = driver.find_element(By.CLASS_NAME, "data-header__headline-wrapper").text
    no, name = no_and_name.split(" ", 1)
    player['no'] = no[1:]
    player['name'] = name
    return player


def do_scraping(driver, logger):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    for league_link in leagues:
        for club_link in get_clubs_of_league(driver, league_link):
            for player_link in get_players_of_club(driver, club_link):
                player = scrape_player(driver, player_link)
                write_player(timestamp, player)


def write_player(timestamp, player):
    print(f"Scraped:\t\t{player['name']}")
    filepath = f"data/players_{timestamp}.csv"
    exists = os.path.exists(filepath)
    with open(filepath, 'a') as f:
        w = csv.DictWriter(f, player.keys())
        if not exists:
            w.writeheader()
        w.writerow(player)


def get_players_of_club(driver, club_link):
    driver.get(club_link)
    players = driver.find_elements(By.XPATH, "//div[@id='yw1']/table/tbody//tr/td[2]/table/tbody/tr/td[2]/a")
    players = list(map(lambda c: c.get_attribute("href"), players))
    return players


def get_clubs_of_league(driver, league_link):
    driver.get(league_link)
    clubs = driver.find_elements(By.XPATH, "//div[@id='yw1']/table/tbody//tr/td[3]/a")
    clubs = list(map(lambda c: c.get_attribute("href"), clubs))
    return clubs


def get_logger():
    logging.basicConfig(filename="transfermarkt_scraper.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger: logging.Logger = logging.getLogger('transfermarkt_scraper')
    return logger


def get_driver():
    options = Options()
    if not show_browser_ui:
        options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver_mac', options=options)
    driver.implicitly_wait(30)
    driver.maximize_window()
    return driver


if __name__ == '__main__':
    run()
