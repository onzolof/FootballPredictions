import csv
import logging
import os
import sys

import yaml
from datetime import datetime
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def run():
    config = load_config()
    driver = get_driver(config)
    init_logger()
    worker_id = sys.argv[1]
    index_start = int(sys.argv[2].split('-')[0])
    index_end = int(sys.argv[2].split('-')[1])
    leagues = config['leagues'][index_start:index_end + 1]
    timestamp = sys.argv[3]
    do_scraping(driver, worker_id, timestamp, leagues, config['enable_instagram_scraping'])
    driver.close()


def do_scraping(driver, worker_id, timestamp, leagues, enable_insta_scraping):
    for league_link in leagues:
        clubs, league_country = get_clubs_of_league(driver, league_link)
        for club_link in clubs:
            for player_link in get_players_of_club(driver, club_link):
                try:
                    player = dict()
                    player['league_country'] = league_country
                    player['scraping_time'] = datetime.now().strftime('%Y%m%d%H%M%S')
                    player['link'] = player_link
                    player = scrape_player(driver, player_link, player, enable_insta_scraping)
                    write_player(worker_id, timestamp, player)
                except BaseException as exception:
                    log_scraping_error(worker_id, timestamp, player_link, exception)
    print('Finished')


def scrape_player(driver, player_link, player, enable_insta_scraping):
    lookup = HtmlLookup(driver)
    interactor = Interactor(driver)

    driver.get(player_link)

    no_and_name = lookup.from_text_by_class('data-header__headline-wrapper')
    if no_and_name.startswith('#'):
        no, name = no_and_name.split(" ", 1)
        player['no'] = no[1:]
        player['name'] = name
    else:
        player['no'] = ''
        player['name'] = no_and_name

    player['league'] = lookup.from_text_by_class('data-header__league')
    player['club'] = lookup.from_text_by_class('data-header__club')

    increment = None
    for index in range(2, 10):
        value = lookup.from_text(f"//main/header/div[{index}]/div/span[3]/span")
        if value:
            player['league_level'] = value
            increment = index - 2
            break

    if increment is not None:
        player['market_value'] = lookup.from_inner_text(f'//*[@id="main"]/main/header/div[{5 + increment}]/a')
        player['market_value_currency'] = lookup.from_inner_text(f'//*[@id="main"]/main/header/div[{5 + increment}]/a/span')
        player['market_value_latest_correction'] = lookup.from_inner_text( f'//*[@id="main"]/main/header/div[{5 + increment}]/a/p')
    else:
        player['league_level'] = ''
        player['market_value'] = ''
        player['market_value_currency'] = ''
        player['market_value_latest_correction'] = ''

    xpath_highest_value = lambda label, element: f"//*[normalize-space(text()) = '" + label + "']//following-sibling::" + element
    player['highest_market_value'] = lookup.from_inner_text(xpath_highest_value('Höchster Marktwert:', 'div[1]'))
    player['highest_market_value_date'] = lookup.from_inner_text(xpath_highest_value('Höchster Marktwert:', 'div[2]'))

    xpath_player_data = lambda label: f"//*[normalize-space(text()) = '" + label + "']//following-sibling::span"
    player['age'] = lookup.from_inner_text(xpath_player_data('Alter:'))
    player['height'] = lookup.from_inner_text(xpath_player_data('Größe:'))
    player['nationality'] = lookup.from_inner_text(xpath_player_data('Nationalität:'))
    player['position'] = lookup.from_inner_text(xpath_player_data('Position:'))
    player['foot'] = lookup.from_inner_text(xpath_player_data('Fuß:'))
    player['consultancy'] = lookup.from_inner_text(xpath_player_data('Spielerberater:'))
    player['supplier'] = lookup.from_inner_text(xpath_player_data('Ausrüster:'))
    player['club_since'] = lookup.from_inner_text(xpath_player_data('Im Team seit:'))
    player['contract_until'] = lookup.from_inner_text(xpath_player_data('Vertrag bis:'))

    xpath_international = lambda label, element: f"//*[normalize-space(text()) = '" + label + "']//child::" + element
    player['international'] = lookup.from_inner_text(xpath_international('Nationalspieler:', 'span') + '/a')
    if not player['international']:
        player['international'] = lookup.from_inner_text(xpath_international('Akt. Nationalspieler:', 'span') + '/a')
    player['former_international'] = lookup.from_inner_text( xpath_international('Ehem. Nationalspieler:', 'span') + '/a')
    player['international_games'] = lookup.from_inner_text(xpath_international('Länderspiele/Tore:', 'a[1]'))
    player['international_goals'] = lookup.from_inner_text(xpath_international('Länderspiele/Tore:', 'a[2]'))

    league_found = interactor.click(f"//*[@id='svelte-performance-data']/div/main/div/div[1]//div/img[@title='{player['league']}']/parent::div")
    if league_found:
        xpath_circle = lambda label: f"//*[normalize-space(text()) = '{label}']//parent::div/div[1]/span"
        player['starting_eleven_quote'] = lookup.from_inner_text(xpath_circle('Startelf-Quote'))
        player['minutes_quote'] = lookup.from_inner_text(xpath_circle('Spielminuten'))

        if player['position'] == 'Torwart':
            player['penalty_saves_quote'] = lookup.from_inner_text(xpath_circle('Elfer abgewehrt'))
            player['goal_participation_quote'] = ''
        else:
            player['penalty_saves_quote'] = ''
            player['goal_participation_quote'] = lookup.from_inner_text(xpath_circle('Torbeteiligungen'))
    else:
        player['starting_eleven_quote'] = ''
        player['minutes_quote'] = ''
        player['penalty_saves_quote'] = ''
        player['goal_participation_quote'] = ''

    player['instagram'] = lookup.from_attribute(xpath_player_data('Social Media:') + '/div//a[@title="Instagram"]', 'href')
    player['injury'] = lookup.from_inner_text('//*[@class="verletzungsbox"]//div[2]')

    performance_data_link = lookup.from_attribute('//*[@id="svelte-performance-data"]/div/main/div/div[2]/a', 'href')
    has_extended_performance_data = False
    if performance_data_link and league_found:
        driver.get(performance_data_link)
        has_extended_performance_data = interactor.click('//*[@id="main"]/main/div[3]/div/div[1]/div[2]/a[2]/div')
        if has_extended_performance_data:
            xpath_performance_data = lambda id: f"//*[@id='yw1']/table/tbody/tr/td[count(//th[@id='{id}']/preceding-sibling::th) + 1]"
            if player['position'] == 'Torwart':
                player['goals_conceded'] = lookup.from_inner_text(xpath_performance_data('yw1_c13'))
                player['clean_sheets'] = lookup.from_inner_text(xpath_performance_data('yw1_c14'))
                player['games'] = lookup.from_inner_text(xpath_performance_data('yw1_c4'))
                player['points_per_game'] = lookup.from_inner_text(xpath_performance_data('yw1_c5'))
                player['goals'] = lookup.from_inner_text(xpath_performance_data('yw1_c6'))
                player['assists'] = ''
                player['own_goals'] = lookup.from_inner_text(xpath_performance_data('yw1_c7'))
                player['ins'] = lookup.from_inner_text(xpath_performance_data('yw1_c8'))
                player['outs'] = lookup.from_inner_text(xpath_performance_data('yw1_c9'))
                player['yellow_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c10'))
                player['yellow_red_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c11'))
                player['red_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c12'))
                player['penalty_goals'] = ''
                player['minutes_per_goal'] = ''
                player['minutes'] = lookup.from_inner_text(xpath_performance_data('yw1_c15'))
            else:
                player['goals_conceded'] = ''
                player['clean_sheets'] = ''
                player['games'] = lookup.from_inner_text(xpath_performance_data('yw1_c4'))
                player['points_per_game'] = lookup.from_inner_text(xpath_performance_data('yw1_c5'))
                player['goals'] = lookup.from_inner_text(xpath_performance_data('yw1_c6'))
                player['assists'] = lookup.from_inner_text(xpath_performance_data('yw1_c7'))
                player['own_goals'] = lookup.from_inner_text(xpath_performance_data('yw1_c8'))
                player['ins'] = lookup.from_inner_text(xpath_performance_data('yw1_c9'))
                player['outs'] = lookup.from_inner_text(xpath_performance_data('yw1_c10'))
                player['yellow_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c11'))
                player['yellow_red_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c12'))
                player['red_cards'] = lookup.from_inner_text(xpath_performance_data('yw1_c13'))
                player['penalty_goals'] = lookup.from_inner_text(xpath_performance_data('yw1_c14'))
                player['minutes_per_goal'] = lookup.from_inner_text(xpath_performance_data('yw1_c15'))
                player['minutes'] = lookup.from_inner_text(xpath_performance_data('yw1_c16'))

    if not performance_data_link or not has_extended_performance_data:
        player['goals_conceded'] = ''
        player['clean_sheets'] = ''
        player['games'] = ''
        player['points_per_game'] = ''
        player['goals'] = ''
        player['assists'] = ''
        player['own_goals'] = ''
        player['ins'] = ''
        player['outs'] = ''
        player['yellow_cards'] = ''
        player['yellow_red_cards'] = ''
        player['red_cards'] = ''
        player['penalty_goals'] = ''
        player['minutes_per_goal'] = ''
        player['minutes'] = ''

    if enable_insta_scraping:
        if player['instagram']:
            driver.get(player['instagram'])
            player['instagram_posts'] = lookup.from_inner_text(f"//main/div/header/section/ul/li[1]/button/span")
            player['instagram_followers'] = lookup.from_attribute(f"//main/div/header/section/ul/li[2]/button/span",
                                                                  'title')
        else:
            player['instagram_posts'] = ''
            player['instagram_followers'] = ''

    return player


def load_config():
    with open("config.yaml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


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


def write_player(worker_id, timestamp, player):
    print(f"Scraped:\t{player['league']}\t{player['club']}\t{player['name']}")
    filepath = f"scraped_data/players_{timestamp}_{worker_id}.csv"
    exists = os.path.exists(filepath)
    with open(filepath, 'a') as f:
        w = csv.DictWriter(f, player.keys(), delimiter=";")
        if not exists:
            w.writeheader()
        w.writerow(player)


def log_scraping_error(worker_id, timestamp, player_link, exception):
    print(f"Error:\t{player_link}\t{str(exception)}")
    filepath = f"scraped_data/errors_{timestamp}_{worker_id}.csv"
    with open(filepath, 'a') as f:
        f.write(player_link + '\n')


def init_logger():
    logging.basicConfig(filename="transfermarkt_scraper.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger: logging.Logger = logging.getLogger('transfermarkt_scraper')
    return logger


def get_driver(config):
    options = Options()
    if not config['show_browser_ui']:
        options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(config['driver_implicitly_wait'])
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
