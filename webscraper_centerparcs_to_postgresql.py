# Import necessary modules from Selenium and other packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium.common.exceptions import NoSuchElementException
import time
import csv
import psycopg2
from psycopg2 import sql

# Define function to get data from Center Parcs website

def get_data(url) -> list:
    # Set Chrome options to run headlessly (without a GUI)
    browser_options = ChromeOptions()
    browser_options.headless = False
    # Initialize Chrome driver and navigate to provided URL
    driver = Chrome(options=browser_options)
    driver.get(url)
    time.sleep(5)
    country = driver.find_element(By.CSS_SELECTOR, "div.domainBanner-locationTitle")
    vacation_parc = driver.find_element(By.CSS_SELECTOR, "span.domainBanner-titleParkLabelName")
    # Click button to show all available cottages until it is no longer visible
    while True:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.js-seeMore'))
            )
            element.click()
            time.sleep(5)
        except:
            break
    # Find information about each cottage on the page
    cottages = driver.find_elements(By.CSS_SELECTOR, "div.accCart-informationContainer")
    data = []

    # For each cottage, extract relevant information and add to a dictionary
    for cottage in cottages:
        title = cottage.find_element(By.CSS_SELECTOR, "div.accCart-title")
        try:
            new_price = cottage.find_element(By.CSS_SELECTOR, "span.accCart-price")
        except NoSuchElementException:
            continue
        amount = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem")
        date = cottage.find_element(By.CSS_SELECTOR, "div.accCart-duration")
        bedroom = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(2)")
        surface = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(3)")
        cottage_item = {
            'title': title.text,
            'price': new_price.text,
            'amount_of_persons': amount.text,
            'bedroom': bedroom.text,
            'duration': date.text,
            'surface': surface.text,
            'country': country.text,
            'vacation_parc': vacation_parc.text
        }
        data.append(cottage_item)

        # Connect to PostgreSQL database
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="CenterParcsDB",
            user="postgres",
            password="WouterV"
        )
        cur = conn.cursor()

        # Insert data into PostgreSQL database
        for item in data:
            table_name = sql.Identifier('cottages')
            columns = sql.SQL(',').join(map(sql.Identifier, item.keys()))
            values = sql.SQL(',').join(sql.Placeholder() * len(item))
            insert_query = sql.SQL("INSERT INTO {0} ({1}) VALUES ({2})").format(
                table_name, columns, values
            )
            cur.execute(insert_query, list(item.values()))

        # Commit changes and close the connection
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    driver.quit()
    return data

def main():
    #user inputs that need to be filled in for the url
    country = input("Enter a country: ")
    vacation_park = input("Enter a vacation park name: ")
    vacation_park_code = input("Enter a vacation park code: ")
    #url to the page that needs to be scraped
    url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?market=be&language=vl&c=CPE_PRODUCT&univers=cpe&type=PRODUCT_COTTAGES&item=HB&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=30&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[DISPO]=-1&facet[COUNTRYSITE][]=l2_HB&facet[PARTICIPANTSCP][adult]=2"
    data = get_data(url)

    # write data to csv file
    with open(f"{country}/{vacation_park}_cottages.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    # Print a message indicating the number of scraped cottages and the location of the CSV file
    print(f"{len(data)} cottages scraped and saved to {vacation_park}_cottages.csv in the {country} folder")
# If this script is being run as the main module, call the main function
if __name__ == '__main__':
    main()