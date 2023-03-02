from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo import MongoClient


client = MongoClient('127.0.0.1', 27017)
db = client['base_mvideo']
trends_db = db.mvideo_trends

chrome_options = Options()
chrome_options.add_argument("--windows-size=1920,1080")
driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
driver.implicitly_wait(15)

url = 'https://www.mvideo.ru'
driver.get(url)
driver.execute_script("window.scrollTo(0, window.scrollY + 1600)")


buttons = driver.find_elements(By.CLASS_NAME, 'tab-button')

button_trend = buttons[1]
button_trend.click()
trends = driver.find_element(By.XPATH, "//mvid-shelf-group[@class='page-carousel-padding ng-star-inserted']")


while True:
    try:
        button_next = trends.find_element(By.XPATH, "//mvid-carousel[@class='carusel ng-star-inserted']"
                                                    "//button[@class='btn forward mv-icon-button--primary "
                                                    "mv-icon-button--shadow mv-icon-button--medium "
                                                    "mv-button mv-icon-button']")
        button_next.click()
    except:
        break


goods = buttons[0].find_elements(By.XPATH, "./ancestor::mvid-shelf-group")
names = goods[0].find_elements(By.XPATH, "//div[@class='title']")
links = goods[0].find_elements(By.XPATH, "//div[@class='title']/a[@href]")
rating_list = goods[0].find_elements(By.XPATH, "//span[@class='rating-value medium']")
prices = goods[0].find_elements(By.XPATH, "//span[@class='price__main-value']")

item = {}
for name, rating, link, price in zip(names, rating_list, links, prices):

    item['name'] = name.text
    item['rating'] = rating.text
    item['link'] = link.get_attribute("href")
    item['price'] = price.text

    trends_db.update_one({'link': item['link']}, {'$set': item}, upsert=True)


driver.quit()
