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
        clubs, league_country = get_clubs_of_league(driver, league_link)
        for club_link in clubs:
            for player_link in get_players_of_club(driver, club_link):
                try:
                    player = scrape_player(driver, player_link)
                    player['league_country'] = league_country
                    player['scraping_time'] = timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    write_player(timestamp, player)
                except BaseException as exception:
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

    # todo: fix this
    # player['league_level'] = driver.find_element(By.XPATH, "//*[@id='main']/main/header/div[2]/div/span[3]/span").text
    # player['club_since'] = driver.find_element(By.XPATH, "//main/header//div[3]//div//span[4]/span").text
    # player['contract_until'] = driver.find_element(By.XPATH, "//main/header//div[3]//div//span[5]/span").text

    # todo: find_element might return nothing -> fix this everywhere
    player['age'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[6]").get_attribute('innerText').strip()
    player['height'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[8]").get_attribute('innerText').strip()
    player['nationality'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[10]").get_attribute('innerText').strip()
    player['position'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[12]").get_attribute('innerText').strip()
    player['foot'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[14]").get_attribute('innerText').strip()
    player['consultancy'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[16]/a").get_attribute('innerText').strip()
    player['supplier'] = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[26]").get_attribute('innerText').strip()

    player['international'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[5]/div/ul[3]/li[1]/span/a').get_attribute('innerText').strip()
    player['international_games'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[5]/div/ul[3]/li[2]/a[1]').get_attribute('innerText').strip()
    player['international_goals'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[5]/div/ul[3]/li[2]/a[2]').get_attribute('innerText').strip()

    player['market_value'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[6]/a').get_attribute('innerText').strip()
    player['market_value_currency'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[6]/a/span').get_attribute('innerText').strip()
    player['market_value_latest_correction'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/header/div[6]/a/p').get_attribute('innerText').strip()
    player['highest_market_value'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/div[3]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[2]').get_attribute('innerText').strip()
    player['highest_market_value_date'] = driver.find_element(By.XPATH, '//*[@id="main"]/main/div[3]/div[1]/div[2]/div/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[3]').get_attribute('innerText').strip()

    player['games'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[1]/a').get_attribute('innerText').strip()
    player['yellow_cards'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[1]/a').get_attribute('innerText').strip()
    player['yellow_red_cards'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[2]/a').get_attribute('innerText').strip()
    player['red_cards'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[2]/li[3]/a').get_attribute('innerText').strip()

    player['starting_eleven'] = driver.find_element(By.XPATH, '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[1]/div//span[1]').get_attribute('innerText').strip()
    player['minutes'] = driver.find_element(By.XPATH, '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[2]/div//span[1]').get_attribute('innerText').strip()

    if player['position'] == 'Torwart':
        player['goals_conceded'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[2]/a').get_attribute('innerText').strip()
        player['clean_sheets'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[3]/a').get_attribute('innerText').strip()
        player['penalty_saves'] = driver.find_element(By.XPATH, '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[3]/div//span[1]').get_attribute('innerText').strip()
        player['goals'] = ''
        player['assists'] = ''
        player['goal_participation'] = ''
    else:
        player['goals'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[2]/a').get_attribute('innerText').strip()
        player['assists'] = driver.find_element(By.XPATH, '//*[@id="svelte-performance-data"]/div/main/div/div[2]/div[2]/ul[1]/li[3]/a').get_attribute('innerText').strip()
        player['goal_participation'] = driver.find_element(By.XPATH, '//div[@class="tm-player-performance__statistic-gauges svelte-1jbxbl0"]//div[3]/div//span[1]').get_attribute('innerText').strip()
        player['goals_conceded'] = ''
        player['clean_sheets'] = ''
        player['penalty_saves'] = ''

    instagram_link = driver.find_element(By.XPATH, "//div[@class='row']/div/div[2]/div/div[2]/div/span[28]/div/a").get_attribute('href')
    if instagram_link:
        driver.get(instagram_link)
        player['instagram_posts'] = driver.find_element(By.XPATH, '//main/div/header/section/ul/li[1]/button/span').get_attribute('innerText')
        player['instagram_followers'] = driver.find_element(By.XPATH, '//main/div/header/section/ul/li[2]/button/span').get_attribute('title')
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
