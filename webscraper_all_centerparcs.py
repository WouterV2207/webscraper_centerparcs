# Import necessary modules from Selenium and other packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import psycopg2
from psycopg2 import sql

# Define function to get data from Center Parcs website

def get_data_all(url) -> list:
    # Set Chrome options to run headlessly (without a GUI)
    browser_options = ChromeOptions()
    browser_options.headless = True
    # Initialize Chrome driver and navigate to provided URL
    driver = Chrome(options=browser_options)
    driver.get(url)
    time.sleep(5)
    # Click button to show all available cottages until it is no longer visible
    while True:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "span.button--greenWhite"))
            )
            element.click()
            time.sleep(5)
        except:
            break
    # Find information about each cottage on the page
    cottages = driver.find_elements(By.CSS_SELECTOR, "div.accCart")
    data = []
    # For each cottage, extract relevant information and add to a dictionary
    for cottage in cottages:
        title = cottage.find_element(By.CSS_SELECTOR, "div.accCart-title")
        new_price = cottage.find_element(By.CSS_SELECTOR, "span.accCart-price")
        amount = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem")
        date = cottage.find_element(By.CSS_SELECTOR, "div.accCart-duration")
        bedroom = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(2)")
        surface = cottage.find_element(By.CSS_SELECTOR, "li.accCart-specificationsItem:nth-child(3)")
        country = cottage.find_element(By.CSS_SELECTOR, "p.cartouche-geo")
        vacation_parc = cottage.find_element(By.CSS_SELECTOR, "span.titleDomain")
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
    #url to the page that needs to be scraped
    url = "https://www.centerparcs.be/be-vl/last-minutes_sck"
    data = get_data_all(url)
    print(f"{len(data)} cottages scraped and saved to database")

# If this script is being run as the main module, call the main function
if __name__ == '__main__':
    main()