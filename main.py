import csv
import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

show_browser_ui = False
enable_instagram_scraping = False
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
                    player = dict()
                    player['league_country'] = league_country
                    player['scraping_time'] = datetime.now().strftime('%Y%m%d%H%M%S')
                    player['link'] = player_link
                    player = scrape_player(driver, player_link, player)
                    write_player(timestamp, player)
                except BaseException as exception:
                    log_scraping_error(timestamp, player_link, exception)


def scrape_player(driver, player_link, player):
    lookup = HtmlLookup(driver)
    interactor = Interactor(driver)

    driver.get(player_link)

    no_and_name = lookup.from_text_by_class('data-header__headline-wrapper')
    no, name = no_and_name.split(" ", 1)
    player['no'] = no[1:]
    player['name'] = name

    player['league'] = lookup.from_text_by_class('data-header__league')
    player['club'] = lookup.from_text_by_class('data-header__club')

    increment = 0
    for index in range(2, 10):
        value = lookup.from_text(f"//main/header/div[{index}]/div/span[3]/span")
        if value:
            player['league_level'] = value
            increment = index - 2
            break

    player['club_since'] = lookup.from_text(f"//main/header/div[{2 + increment}]/div/span[4]/span")
    player['contract_until'] = lookup.from_text(f"//main/header/div[{2 + increment}]/div/span[5]/span")

    xpath_player_data = lambda label: f"//*[normalize-space(text()) = '" + label + "']//following-sibling::span"
    player['age'] = lookup.from_inner_text(xpath_player_data('Alter:'))
    player['height'] = lookup.from_inner_text(xpath_player_data('Größe:'))
    player['nationality'] = lookup.from_inner_text(xpath_player_data('Nationalität:'))
    player['position'] = lookup.from_inner_text(xpath_player_data('Position:'))
    player['foot'] = lookup.from_inner_text(xpath_player_data('Fuß:'))
    player['consultancy'] = lookup.from_inner_text(xpath_player_data('Spielerberater:'))
    player['supplier'] = lookup.from_inner_text(xpath_player_data('Ausrüster:'))

    xpath_international = lambda label, element: f"//*[normalize-space(text()) = '" + label + "']//child::" + element
    player['international'] = lookup.from_inner_text(xpath_international('Nationalspieler:', 'span') + '/a')
    if not player['international']:
        player['international'] = lookup.from_inner_text(xpath_international('Akt. Nationalspieler:', 'span') + '/a')
    player['former_international'] = lookup.from_inner_text(
        xpath_international('Ehem. Nationalspieler:', 'span') + '/a')
    player['international_games'] = lookup.from_inner_text(xpath_international('Länderspiele/Tore:', 'a[1]'))
    player['international_goals'] = lookup.from_inner_text(xpath_international('Länderspiele/Tore:', 'a[2]'))

    player['market_value'] = lookup.from_inner_text(f'//*[@id="main"]/main/header/div[{5 + increment}]/a')
    player['market_value_currency'] = lookup.from_inner_text(f'//*[@id="main"]/main/header/div[{5 + increment}]/a/span')
    player['market_value_latest_correction'] = lookup.from_inner_text(
        f'//*[@id="main"]/main/header/div[{5 + increment}]/a/p')
    xpath_highest_value = lambda label, element: f"//*[normalize-space(text()) = '" + label + "']//following-sibling::" + element
    player['highest_market_value'] = lookup.from_inner_text(xpath_highest_value('Höchster Marktwert:', 'div[1]'))
    player['highest_market_value_date'] = lookup.from_inner_text(xpath_highest_value('Höchster Marktwert:', 'div[2]'))

    xpath_current_season = lambda label: f"//*[normalize-space(text()) = '{label}']//parent::div/following-sibling::a"
    if interactor.click(f"//*[@id='svelte-performance-data']/div/main/div/div[1]//div/img[@title='{player['league']}']/parent::div"):
        player['games'] = lookup.from_inner_text(xpath_current_season('Spiele'))
        player['yellow_cards'] = lookup.from_inner_text(xpath_current_season('Gelbe-Karten'))
        player['yellow_red_cards'] = lookup.from_inner_text(xpath_current_season('Gelb-Rote Karten'))
        player['red_cards'] = lookup.from_inner_text(xpath_current_season('Rote Karten'))

    xpath_circle = lambda label: f"//*[normalize-space(text()) = '{label}']//parent::div/div[1]/span"
    player['starting_eleven'] = lookup.from_inner_text(xpath_circle('Startelf-Quote'))
    player['minutes'] = lookup.from_inner_text(xpath_circle('Spielminuten'))

    if player['position'] == 'Torwart':
        player['goals_conceded'] = lookup.from_inner_text(xpath_current_season('Gegentore'))
        player['clean_sheets'] = lookup.from_inner_text(xpath_current_season('Zu Null'))
        player['penalty_saves'] = lookup.from_inner_text(xpath_circle('Elfer abgewehrt'))
        player['goals'] = ''
        player['assists'] = ''
        player['goal_participation'] = ''
    else:
        player['goals_conceded'] = ''
        player['clean_sheets'] = ''
        player['penalty_saves'] = ''
        player['goals'] = lookup.from_inner_text(xpath_current_season('Tore'))
        player['assists'] = lookup.from_inner_text(xpath_current_season('Vorlagen'))
        player['goal_participation'] = lookup.from_inner_text(xpath_circle('Torbeteiligungen'))

    player['instagram'] = lookup.from_attribute(xpath_player_data('Social Media:') + '/div//a[@title="Instagram"]',
                                                'href')
    if enable_instagram_scraping:
        if player['instagram']:
            driver.get(player['instagram'])
            player['instagram_posts'] = lookup.from_inner_text(f"//main/div/header/section/ul/li[1]/button/span")
            player['instagram_followers'] = lookup.from_attribute(f"//main/div/header/section/ul/li[2]/button/span",
                                                                  'title')
        else:
            player['instagram_posts'] = ''
            player['instagram_followers'] = ''

    # todo: features to add:
    # - erweiterte detaillierte leistungsdaten aus der vergangenen saison in der liga
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
    print(f"Error:\t\t{player_link}\t\t{str(exception)}")
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
    # todo: overriding timeout necessary (reducing timeout speeds up scraping time significantly but might lead to missing data when having a bad internet connection)
    # driver.implicitly_wait(30)
    driver.maximize_window()
    return driver


class HtmlLookup:
    def __init__(self, driver):
        self._driver = driver

    def from_attribute(self, xpath, attribute):
        return self._try(lambda driver: driver.find_element(By.XPATH, xpath),
                         lambda element: element.get_attribute(attribute))

    def from_inner_text(self, xpath):
        return self.from_attribute(xpath, 'innerText')

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
        return string.replace('\n', '').strip() if string else ''


class Interactor:

    def __init__(self, driver):
        self._driver = driver

    def click(self, xpath):
        try:
            element = self._driver.find_element(By.XPATH, xpath)
            self._driver.execute_script("arguments[0].click();", element)
            return True
        except NoSuchElementException:
            return False


if __name__ == '__main__':
    run()
