# Import necessary modules from Selenium and other packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime 
import time
import csv
import psycopg2
from psycopg2 import sql

def get_data_all(url, program_cat) -> list:
    # Set Chrome options to run headlessly (without a GUI)
    browser_options = ChromeOptions()
    browser_options.headless = False
    # Initialize Chrome driver and navigate to provided URL
    driver = Chrome(options=browser_options)
    driver.get(url)
    time.sleep(5)
    # Click button to show all available cottages until it is no longer visible
    while True:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.js-searchPagination"))
            )
            element.click()
            time.sleep(3)
        except:
            break
    # Find information about each cottage on the page
    cottages = driver.find_elements(By.CSS_SELECTOR, "div.accCart")
    data = []
    # For each cottage, extract relevant information and add to a dictionary
    for cottage in cottages:
        title = cottage.find_element(By.CSS_SELECTOR, "div.accCart-title")
        try:
            new_price = cottage.find_element(By.CSS_SELECTOR, "span.accCart-price")
        except NoSuchElementException:
            continue
        try:
            old_price = cottage.find_element(By.CSS_SELECTOR, "div.accCart-priceContainer del")
        except NoSuchElementException:
            old_price = None
        amount = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem")
        date = cottage.find_element(By.CSS_SELECTOR, "div.accCart-duration")
        bedroom = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(2)")
        surface = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(3)")
        country = cottage.find_element(By.CSS_SELECTOR, "p.cartouche-geo")
        vacation_parc = cottage.find_element(By.CSS_SELECTOR, "span.titleDomain")
        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
        cottage_item = {
            'title': title.text,
            'new_price': new_price.text,
            'old_price': old_price.text if old_price else '',
            'amount_of_persons': amount.text,
            'bedroom': bedroom.text,
            'duration': date.text,
            'surface': surface.text,
            'country': country.text,
            'vacation_parc': vacation_parc.text,
            'timestamp': str_date_time,
            'discount_in_euros': int(old_price.text.replace(',', '').replace('€', '')) - int(new_price.text.replace(',', '').replace('€', '')) if old_price else 0, # calculate discount and convert to int
            'discount_in_percent': 0  # initialize discount_in_percent to 0
        }
        if old_price is not None:
            discount_percent = (int(old_price.text.replace(',', '').replace('€', '')) - int(new_price.text.replace(',', '').replace('€', ''))) / int(old_price.text.replace(',', '').replace('€', '')) * 100
            cottage_item['discount_in_percent'] = int(discount_percent)  # assign discount percent to the 'discount_in_percent' key
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
            table_name = sql.Identifier(f'{program_cat}')
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
    try:
        cottages = driver.find_elements(By.CSS_SELECTOR, "div.accCart-informationContainer")
        data = []
    except NoSuchElementException:
            raise Exception("Error: could not extract cottage information")

    # For each cottage, extract relevant information and add to a dictionary
    for cottage in cottages:
        title = cottage.find_element(By.CSS_SELECTOR, "div.accCart-title")
        try:
            new_price = cottage.find_element(By.CSS_SELECTOR, "span.accCart-price")
        except NoSuchElementException:
            continue
        try:
            old_price = cottage.find_element(By.CSS_SELECTOR, "div.accCart-priceContainer del")
        except NoSuchElementException:
            old_price = None
        amount = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem")
        date = cottage.find_element(By.CSS_SELECTOR, "div.accCart-duration")
        bedroom = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(2)")
        surface = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(3)")
        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
        cottage_item = {
            'title': title.text,
            'new_price': int(new_price.text.replace(',', '').replace('€', '')), # remove currency symbol and convert to int
            'old_price': int(old_price.text.replace(',', '').replace('€', '')) if old_price else 0, # remove currency symbol and convert to int
            'amount_of_persons': amount.text,
            'bedroom': bedroom.text,
            'duration': date.text,
            'surface': surface.text,
            'country': country.text,
            'vacation_parc': vacation_parc.text,
            'timestamp': str_date_time,
            'discount_in_euros': int(old_price.text.replace(',', '').replace('€', '')) - int(new_price.text.replace(',', '').replace('€', '')) if old_price else 0, # calculate discount and convert to int
            'discount_in_percent': 0  # initialize discount_in_percent to 0
        }
        if old_price is not None:
            discount_percent = (int(old_price.text.replace(',', '').replace('€', '')) - int(new_price.text.replace(',', '').replace('€', ''))) / int(old_price.text.replace(',', '').replace('€', '')) * 100
            cottage_item['discount_in_percent'] = int(discount_percent)  # assign discount percent to the 'discount_in_percent' key
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
    program_repeater = int(input("How many times do you want to run the program? "))
    for i in range(int(program_repeater)):
        program = input("Where do you want to scrape cottages (resort, country, offer/vacation): ")
        if program == ("resort"):
            program_person = input("Do you want to fill in a specific amount of persons, yes or no (max. 12): ")
            if program_person == ("yes"):
                am_adults = input("How many adults? ")
                am_pets = input("How many pets? (max. 2)")
                am_seniors = input("How many seniors? ")
                am_children = int(input("How many children? "))
                children_ages = []
                for i in range(int(am_children)):
                    age = input(f"Enter age of child (max. 12){i+1}: ")
                    children_ages.append(age)
            else:
                am_adults = 0
                am_pets = 0
                am_seniors = 0
                am_children = 0
                children_ages = []
            program_date = input("Do you want to fill in a specific date, yes or no: ")
            if program_date == ("yes"):
                arr_date = input("fill in an arrival date, yyyy-mm-dd: ")
                ret_date = input("fill in a return date, yyyy-mm-dd: ")
                country = input("Enter a country: ")
                vacation_park = input("Enter a vacation park name: ")
                vacation_park_code = input("Enter a vacation park code: ")
                #url to the page that needs to be scraped
                url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?market=be&language=vl&c=CPE_PRODUCT&univers=cpe&type=PRODUCT_COTTAGES&item=TH&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=30&displayPrice=default&dateuser=1&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[DISPO]=-1&facet[DATE]={arr_date}&facet[DATEEND]={ret_date}&facet[COUNTRYSITE][]=l2_TH&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
            if program_date == ("no"):
                country = input("Enter a country: ")
                vacation_park = input("Enter a vacation park name: ")
                vacation_park_code = input("Enter a vacation park code: ")
                #url to the page that needs to be scraped
                url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?market=be&language=vl&c=CPE_PRODUCT&univers=cpe&type=PRODUCT_COTTAGES&item=HB&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=30&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[DISPO]=-1&facet[COUNTRYSITE][]=l2_HB&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
            data = get_data(url)

        # write data to csv file
            with open(f"{country}/{vacation_park}_cottages.csv", mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        # Print a message indicating the number of scraped cottages and the location of the CSV file
            print(f"{len(data)} cottages scraped and saved to {vacation_park}_cottages.csv in the {country} folder")
        if program == ("offer/vacation"):
            program_cat = input("Do you want to scrape vacation or offer? ")
            #url to the page that needs to be scraped
            if program_cat == ("offer"):
                offer = input("What type of offer (last-minutes, ecocheques, vroegboekvoordeel, familie-55plus-korting, flexibel-boeken, weekendje-weg-voorjaar)? ")
                url = f"https://www.centerparcs.be/be-vl/{offer}_sck?market=be&language=vl&c=CPE_SINGLECLICK_V3&univers=cpe&type=SINGLECLICK_V3&item=280&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[HOUSINGCATEGORY][]=25&facet[HOUSINGCATEGORY][]=31&facet[HOUSINGCATEGORY][]=32&facet[HOUSINGCATEGORY][]=33&facet[HOUSINGCATEGORY][]=37&facet[HOUSINGCATEGORY][]=64&facet[HOUSINGCATEGORY][]=65&facet[PARTICIPANTSCP][adult]=2"
            if program_cat == ("vacation"):
                vacation = input("What type of vacation (paasvakantie, hemelvaart-weekend-weg, pinksteren-weekend-weg, zomervakantie, herfstvakantie, 11-november, kerstvakantie, krokusvakantie)? ")
                url = f"https://www.centerparcs.be/be-vl/{vacation}_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=695&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[HOUSINGCATEGORY][]=25&facet[HOUSINGCATEGORY][]=31&facet[HOUSINGCATEGORY][]=32&facet[HOUSINGCATEGORY][]=33&facet[HOUSINGCATEGORY][]=64&facet[HOUSINGCATEGORY][]=65&facet[DATE]=2023-03-31&facet[DATEEND]=2023-04-14&facet[PARTICIPANTSCP][adult]=2"
            data = get_data_all(url, program_cat)
            if program_cat == ("offer"):
                with open(f"offer/{offer}.csv", mode="w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                with open(f"vacation/{vacation}.csv", mode="w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            print(f"{len(data)} cottages scraped and saved to database")
        if program == ("country"):
            program_cat = "cottages"
            scrape_country = input("Which country? (BE, NL, DE, FR) ")
            program_person = input("Do you want to fill in a specific amount of persons, yes or no (max. 12): ")
            if program_person == ("yes"):
                am_adults = input("How many adults? ")
                am_pets = input("How many pets? (max. 2)")
                am_seniors = input("How many seniors? ")
                am_children = int(input("How many children? "))
                children_ages = []
                for i in range(int(am_children)):
                    age = input(f"Enter age of child (max. 12){i+1}: ")
                    children_ages.append(age)
            else:
                am_adults = 0
                am_pets = 0
                am_seniors = 0
                am_children = 0
                children_ages = []
            program_date = input("Do you want to fill in a specific date, yes or no: ")
            if program_date == ("yes"):
                arr_date = input("fill in an arrival date, yyyy-mm-dd: ")
                ret_date = input("fill in a return date, yyyy-mm-dd: ")
                #url to the page that needs to be scraped
                url = f"https://www.centerparcs.be/be-vl/vakantieparken-belgie_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=561&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=1&facet[DATE]={arr_date}&facet[DATEEND]={ret_date}&facet[COUNTRYSITE][]=l1_{scrape_country}&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
            if program_date == ("no"):
                #url to the page that needs to be scraped
                url = f"https://www.centerparcs.be/be-vl/vakantieparken-belgie_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=561&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[COUNTRYSITE][]=l1_{scrape_country}&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
        # url = f"https://www.centerparcs.be/be-vl/vakantieparken-belgie_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=536&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[COUNTRYSITE][]=l1_{scrape_country}&facet[PARTICIPANTSCP][adult]=2"
            data = get_data_all(url, program_cat)
            with open(f"countries/{scrape_country}.csv", mode="w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)  
            print(f"{len(data)} cottages scraped and saved to database")

# If this script is being run as the main module, call the main function
if __name__ == '__main__':
    main()