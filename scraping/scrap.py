import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from params.params import Params


def web_scraping(soup):
    list_urls = []
    for org in soup.findAll('a', id='wc-endpoint'):
        name = org.find(class_='yt-simple-endpoint').get('href')
        link = "".join([Params().Y_B, name])
        list_urls.append(link)
    return list_urls


def get_browser(links):
    o = Options()
    o.add_argument(Params().USER_AGENT)
    o.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=o)
    browser.get(links)
    time.sleep(5)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    browser.close()
    return soup
