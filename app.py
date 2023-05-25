import csv
from flask import Flask, render_template, request

from webscraper_full import get_data
from webscraper_full import get_data_all

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
   if request.method == 'POST':
       program = request.form['program']
       if program == "resort":
            program_date = request.form['program_date']
            country = request.form['country']
            vacation_park_code = request.form['vacation_park_code']
            vacation_park = request.form['vacation_park']
            arr_date = request.form['arr_date']
            ret_date = request.form['ret_date']
            am_adults = request.form['am_adults']
            am_seniors = request.form['am_seniors']
            am_pets = request.form['am_pets']
            am_children = request.form['am_children']
            children_ages = []
            for i in range(int(am_children)):
                children_ages = request.form['children_ages']
                {i + 1}
            if program_date == "yes":
                url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?market=be&language=vl&c=CPE_PRODUCT&univers=cpe&type=PRODUCT_COTTAGES&item=TH&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=30&displayPrice=default&dateuser=1&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[DISPO]=-1&facet[DATE]={arr_date}&facet[DATEEND]={ret_date}&facet[COUNTRYSITE][]=l2_TH&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
            else:
                url = f"https://www.centerparcs.be/be-vl/{country}/fp_{vacation_park_code}_vakantiepark-{vacation_park}/cottages?market=be&language=vl&c=CPE_PRODUCT&univers=cpe&type=PRODUCT_COTTAGES&item=HB&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=30&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[DISPO]=-1&facet[COUNTRYSITE][]=l2_HB&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
            data = get_data(url)
            filename = f"{vacation_park}.csv"
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return render_template('index2.html', message=f"Data scraped and saved as {filename}")
       elif program == "offer/vacation":
           program_cat = request.form['program_cat']
           offer = request.form['offer']
           vacation = request.form['vacation']
           if (program_cat == "offer"):
               url = f"https://www.centerparcs.be/be-vl/{offer}_sck?market=be&language=vl&c=CPE_SINGLECLICK_V3&univers=cpe&type=SINGLECLICK_V3&item=280&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[HOUSINGCATEGORY][]=25&facet[HOUSINGCATEGORY][]=31&facet[HOUSINGCATEGORY][]=32&facet[HOUSINGCATEGORY][]=33&facet[HOUSINGCATEGORY][]=37&facet[HOUSINGCATEGORY][]=64&facet[HOUSINGCATEGORY][]=65&facet[PARTICIPANTSCP][adult]=2"
               data = get_data_all(url, program_cat)
               filename = f"{offer}.csv"
               with open(filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
           else:
               url = f"https://www.centerparcs.be/be-vl/{vacation}_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=695&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[HOUSINGCATEGORY][]=COMFORT&facet[HOUSINGCATEGORY][]=PREMIUM&facet[HOUSINGCATEGORY][]=VIP&facet[HOUSINGCATEGORY][]=EXCLUSIVE&facet[HOUSINGCATEGORY][]=25&facet[HOUSINGCATEGORY][]=31&facet[HOUSINGCATEGORY][]=32&facet[HOUSINGCATEGORY][]=33&facet[HOUSINGCATEGORY][]=64&facet[HOUSINGCATEGORY][]=65&facet[DATE]=2023-03-31&facet[DATEEND]=2023-04-14&facet[PARTICIPANTSCP][adult]=2"
               data = get_data_all(url, program_cat)
               filename = f"{vacation}.csv"
               with open(filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
               return render_template('index2.html', message=f"Data scraped and saved as {filename}")
       elif program == "country":
           program_cat = "cottages"
           scrape_country = request.form['scrape_country']
           program_date = request.form['program_date']
           arr_date = request.form['arr_date']
           ret_date = request.form['ret_date']
           am_adults = request.form['am_adults']
           am_seniors = request.form['am_seniors']
           am_pets = request.form['am_pets']
           am_children = request.form['am_children']
           children_ages = []
           for i in range(int(am_children)):
                children_ages = request.form['children_ages']
                {i + 1}
           if program_date == "yes":
                url = f"https://www.centerparcs.be/be-vl/vakantieparken-belgie_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=561&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=1&facet[DATE]={arr_date}&facet[DATEEND]={ret_date}&facet[COUNTRYSITE][]=l1_{scrape_country}&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
           else:
                url = f"https://www.centerparcs.be/be-vl/vakantieparken-belgie_sck?market=be&language=vl&c=CPE_SINGLECLICK&univers=cpe&type=SINGLECLICK&item=561&currency=EUR&group=housing&sort=popularity_housing&asc=asc&page=1&nb=10&displayPrice=default&dateuser=0&facet[COUNTRYSITE][]=l1_{scrape_country}&facet[PARTICIPANTSCP][adult]={am_adults}&facet[PARTICIPANTSCP][senior]={am_seniors}&facet[PARTICIPANTSCP][pet]={am_pets}"
                for age in children_ages:
                    url += f"&facet[PARTICIPANTSCP][ages][]={age}"
           data = get_data_all(url, program_cat)
           filename = f"{scrape_country}.csv"
           with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
           return render_template('index2.html', message=f"Data scraped and saved as {filename}")
       return render_template('index2.html', message=None)
   return render_template('index2.html', message=None)
if __name__ == '__main__':
    app.run()