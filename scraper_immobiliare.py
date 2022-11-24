# Import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

url = 'https://www.immobiliare.it/mercato-immobiliare/'
page = requests.get(url)

soup = BeautifulSoup(page.text, 'lxml')

table_regioni = soup.find("table", {"class": "nd-table nd-table--borderBottom"})

headers = []
for i in table_regioni.find_all('th'):
 title = i.text
 headers.append(title)

data_regioni = pd.DataFrame(columns = headers)

for j in table_regioni.find_all('tr')[1:]:
 row_data = j.find_all('td')
 row = [i.text for i in row_data]
 length = len(data_regioni)
 data_regioni.loc[length] = row

regioni_list = data_regioni["Regioni"].values.tolist()

data_province_regioni = pd.DataFrame(columns = ['Comuni', 'Vendita(€/m²)', 'Affitto(€/m²)', 'Provincia'])

# Scraping su regioni
for regione in regioni_list:
    time.sleep(5)
    url = str('https://www.immobiliare.it/mercato-immobiliare/' + regione.lower().replace(" ", "-").replace("'", "-").strip(" "))
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    table_province_regione = soup.find("table", {"class": "nd-table nd-table--borderBottom"})
    
    headers = []
    for i in table_province_regione.find_all('th'):
        title = i.text
        headers.append(title)
    
    data_province_regione = pd.DataFrame(columns = headers)
    
    for j in table_province_regione.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(data_province_regione)
        data_province_regione.loc[length] = row

    if regione == "Valle d'Aosta":
        province_regione_list = ["Aosta"]
    else:
        province_regione_list = data_province_regione["Province"].values.tolist()
    print(province_regione_list)

    # Scraping su province
    
    for provincia in province_regione_list:
        time.sleep(5)
        if provincia == "San Marino":
            pass
        if provincia == "L'Aquila":
            provincia = "Aquila"
        url = str('https://www.immobiliare.it/mercato-immobiliare/' + regione.lower().replace(" ", "-").replace("'", "-") + "/" + provincia.lower().replace(" ", "-").replace("'", "-").replace("-e-","-") + "-provincia")
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        table_comuni_provincia = soup.find("table", {"class": "nd-table nd-table--borderBottom"})

        headers = []
        for i in table_comuni_provincia.find_all('th'):
            title = i.text
            headers.append(title)
            
        data_comuni_provincia = pd.DataFrame(columns = headers)

        for j in table_comuni_provincia.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            length = len(data_comuni_provincia)
            data_comuni_provincia.loc[length] = row
        print(provincia)
        print(len(data_comuni_provincia))
        data_comuni_provincia["Provincia"] = [provincia]*len(data_comuni_provincia)
        
        data_province_regioni = pd.concat([data_province_regioni, data_comuni_provincia]).reset_index(drop=True)
    
data_tot = data_province_regioni

data_tot = data_tot.replace('-', np.NaN)
data_tot['Vendita(€/m²)'] = data_tot['Vendita(€/m²)'].str.replace('[^\d,]', '')\
                  .str.replace(',', '.').astype(float)
data_tot['Affitto(€/m²)'] = data_tot['Affitto(€/m²)'].str.replace('[^\d,]', '')\
                  .str.replace(',', '.').astype(float)

data_tot.to_csv('output/comuni_data.csv', encoding = 'utf-8-sig', index = False, sep = ";")
        
comuni_list = data_tot["Comuni"].values.tolist()