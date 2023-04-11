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
    do_scraping(driver)
    driver.close()


def do_scraping(driver):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    for league_link in leagues:
        for club_link in get_clubs_of_league(driver, league_link):
            for player_link in get_players_of_club(driver, club_link):
                try:
                    player = scrape_player(driver, player_link)
                    write_player(timestamp, player)
                except:
                    log_scraping_error(timestamp, player_link)


def scrape_player(driver, player_link):
    player = dict()
    driver.get(player_link)

    no_and_name = driver.find_element(By.CLASS_NAME, "data-header__headline-wrapper").text
    no, name = no_and_name.split(" ", 1)
    player['no'] = no[1:]
    player['name'] = name

    player['league'] = driver.find_element(By.CLASS_NAME, "data-header__league").text
    player['club'] = driver.find_element(By.CLASS_NAME, "data-header__club").text
    # player['team_since'] = driver.find_element(By.XPATH, "//div[@class='large-6 large-pull-6 small-12 columns spielerdatenundfakten']//span[@class='info-table__content info-table__content--bold'][8]").text

    # todo: features to add:
    # - ligahöhe
    # - im team seit
    # - vertrag bis
    # - alter
    # - nationalität
    # - groesse
    # - position
    # - nationalspieler
    # - laenderspiele
    # - tore in laenderspielen
    # - marktwert in chf
    # - torwart: gegentore & zu null
    # - andere positionen: tore & vorlagen
    # - gelbe karten
    # - gelbrote karten
    # - rote karten
    # - startelf-quote
    # - spielminuten
    # - elfer abgewehrt (torwart)
    # - torbeteiligungen (andere positionen)
    # - fuss
    # - spielerberater
    # - ausrüster
    # - erweiterte detaillierte leistungsdaten aus der vergangenen saison in der liga
    # - insta-followers
    # - fifa-score

    return player


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


def write_player(timestamp, player):
    print(f"Scraped:\t\t{player['league']}\t{player['name']}\t{player['no']}\t{player['club']}\t{player['team_since']}")
    filepath = f"data/players_{timestamp}.csv"
    exists = os.path.exists(filepath)
    with open(filepath, 'a') as f:
        w = csv.DictWriter(f, player.keys())
        if not exists:
            w.writeheader()
        w.writerow(player)


def log_scraping_error(timestamp, player_link):
    print(f"Error:\t\t{player_link}")
    filepath = f"data/errors_{timestamp}.csv"
    with open(filepath, 'a') as f:
        f.write(player_link + '\n')


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
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(30)
    driver.maximize_window()
    return driver


if __name__ == '__main__':
    run()
