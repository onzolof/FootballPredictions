import csv
import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.common import NoSuchElementException
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
        clubs, league_country = get_clubs_of_league(driver, league_link)
        for club_link in clubs:
            for player_link in get_players_of_club(driver, club_link):
                try:
                    player = scrape_player(driver, player_link)
                    player['league_country'] = league_country
                    player['scraping_time'] = timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    write_player(timestamp, player)
                except BaseException as exception:
                    log_scraping_error(timestamp, player_link, exception)


def scrape_player(driver, player_link):
    player = dict()
    lookup = HtmlLookup(driver)

    driver.get(player_link)

    no_and_name = lookup.from_text_by_class('data-header__headline-wrapper')
    no, name = no_and_name.split(" ", 1)
    player['no'] = no[1:]
    player['name'] = name

    player['league'] = lookup.from_text_by_class('data-header__league')
    player['club'] = lookup.from_text_by_class('data-header__club')

    player['league_level'] = lookup.from_text("//main/header/div[3]/div/span[3]/span")
    player['club_since'] = lookup.from_text("//main/header//div[3]//div//span[4]/span")
    player['contract_until'] = lookup.from_text("//main/header//div[3]//div//span[5]/span")

    player['age'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[6]")
    player['height'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[8]")
    player['nationality'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[10]")
    player['position'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[12]")
    player['foot'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[14]")
    player['consultancy'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[16]/a")
    player['supplier'] = lookup.from_inner_text("//div[@class='row']/div/div[2]/div/div[2]/div/span[26]")

    player['international'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[5]/div/ul[3]/li[1]/span/a')
    player['international_games'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[5]/div/ul[3]/li[2]/a[1]')
    player['international_goals'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[5]/div/ul[3]/li[2]/a[2]')

    player['market_value'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[6]/a')
    player['market_value_currency'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[6]/a/span')
    player['market_value_latest_correction'] = lookup.from_inner_text('//*[@id="main"]/main/header/div[6]/a/p')
    player['highest_market_value'] = lookup.from_inner_text(
        '//*[@id="main"]/main/div[3]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[2]')
    player['highest_market_value_date'] = lookup.from_inner_text(
        '//*[@id="main"]/main/div[3]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[3]')

    player['games'] = lookup.from_inner_text(
        '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[1]/a')
    player['yellow_cards'] = lookup.from_inner_text(
        '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[1]/a')
    player['yellow_red_cards'] = lookup.from_inner_text(
        '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[2]/a')
    player['red_cards'] = lookup.from_inner_text(
        '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[3]/a')

    player['starting_eleven'] = lookup.from_inner_text(
        '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[1]/div//span[1]')
    player['minutes'] = lookup.from_inner_text(
        '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[2]/div//span[1]')

    if player['position'] == 'Torwart':
        player['goals_conceded'] = lookup.from_inner_text(
            '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[2]/a')
        player['clean_sheets'] = lookup.from_inner_text(
            '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[3]/a')
        player['penalty_saves'] = lookup.from_inner_text(
            '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[3]/div//span[1]')
        player['goals'] = ''
        player['assists'] = ''
        player['goal_participation'] = ''
    else:
        player['goals'] = lookup.from_inner_text(
            '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[2]/a')
        player['assists'] = lookup.from_inner_text(
            '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[3]/a')
        player['goal_participation'] = lookup.from_inner_text(
            '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[3]/div//span[1]')
        player['goals_conceded'] = ''
        player['clean_sheets'] = ''
        player['penalty_saves'] = ''

    instagram_link = lookup.from_attribute("//div[@class='row']/div/div[2]/div/div[2]/div/span[28]/div/a", 'href')
    if instagram_link:
        driver.get(instagram_link)
        player['instagram_posts'] = lookup.from_inner_text('//main/div/header/section/ul/li[1]/button/span')
        player['instagram_followers'] = lookup.from_attribute('//main/div/header/section/ul/li[2]/button/span', 'title')
    else:
        player['instagram_posts'] = ''
        player['instagram_followers'] = ''

    # todo: features to add:
    # - erweiterte detaillierte leistungsdaten aus der vergangenen saison in der liga
    # - fifa-score

    for key, value in player.items():
        player[key] = value.replace('\n', '')

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
    league_country = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[2]/div/span[1]/a').get_attribute(
        'innerText').strip()
    return clubs, league_country


def write_player(timestamp, player):
    print(f"Scraped:\t\t{player['league']}\t\t{player['club']}\t\t{player['name']}")
    filepath = f"data/players_{timestamp}.csv"
    exists = os.path.exists(filepath)
    with open(filepath, 'a') as f:
        w = csv.DictWriter(f, player.keys())
        if not exists:
            w.writeheader()
        w.writerow(player)


def log_scraping_error(timestamp, player_link, exception):
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


class HtmlLookup:
    def __init__(self, driver):
        self._driver = driver

    def from_attribute(self, xpath, attribute):
        return self._try(lambda driver: driver.find_element(By.XPATH, xpath),
                         lambda element: element.get_attribute(attribute))

    def from_inner_text(self, xpath):
        return self._try(lambda driver: driver.find_element(By.XPATH, xpath),
                         lambda element: element.get_attribute('innerText'))

    def from_text(self, xpath):
        return self._try(lambda driver: driver.find_element(By.XPATH, xpath), lambda element: element.text)

    def from_text_by_class(self, clazz):
        return self._try(lambda driver: driver.find_element(By.CLASS_NAME, clazz), lambda element: element.text)

    def _try(self, find_element_function, extracting_function):
        try:
            element = find_element_function(self._driver)
            return self._clean(extracting_function(element))
        except NoSuchElementException:
            return ''

    @staticmethod
    def _clean(string):
        return string.replace('\n', '').strip()


if __name__ == '__main__':
    run()
