from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import sqlite3

def get_data(url) -> list:
    browser_options = ChromeOptions()
    browser_options.headless = True
    
    driver = Chrome(options=browser_options)
    driver.get(url)

    time.sleep(5)
    
    element = driver.find_element(By.CSS_SELECTOR, "span.button--greenWhite")
    element.click()

     # Wait for the page to load
    time.sleep(5)

    cottages = driver.find_elements(By.CSS_SELECTOR, "div.accCart-informationContainer")
    data = []
    country = driver.find_element(By.CSS_SELECTOR, "div.domainBanner-locationTitle")
    vacation_parc = driver.find_element(By.CSS_SELECTOR, "span.domainBanner-titleParkLabelName")
    if len(cottages) > 17:
        element = driver.find_element(By.CSS_SELECTOR, "span.button--greenWhite")
        element.click()
    for cottage in cottages:
        title = cottage.find_element(By.CSS_SELECTOR, "div.accCart-title")
        new_price = cottage.find_element(By.CSS_SELECTOR, "span.accCart-price")
        amount = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem")
        date = cottage.find_element(By.CSS_SELECTOR, "div.accCart-duration")
        bedroom = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(2)")
        surface = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(3)")
        cottage_item = {
            'title': title.text,
            'price': new_price.text,
            'amount of persons': amount.text,
            'bedroom': bedroom.text,
            'duration': date.text,
            'surface': surface.text,
            'country': country.text,
            'vacation_parc': vacation_parc.text
        }
        data.append(cottage_item)

            # Insert data into SQLite database
        conn = sqlite3.connect('centerparcsdb.db')
        c = conn.cursor()
        c.execute("INSERT INTO cottages (title, price, amount_of_persons, bedroom, duration, surface, country, vacation_parc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (title.text, new_price.text, amount.text, bedroom.text, date.text, surface.text, country.text, vacation_parc.text))
        conn.commit()
        conn.close()

    driver.quit()
    return data

def main():
    #user inputs that need to be filled in for the url
    country = input("Enter a country: ")
    vacation_park = input("Enter a vacation park name: ")
    vacation_park_code = input("Enter a vacation park code: ")
    #url to the page that needs to be scraped
    url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?facet[PARTICIPANTSCP][adult]=1"
    data = get_data(url)

    # write data to csv file
    with open(f"{country}/{vacation_park}_cottages.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"{len(data)} cottages scraped and saved to {vacation_park}_cottages.csv in the {country} folder")

if __name__ == '__main__':
    main()