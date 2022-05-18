from numpy import False_
from spyre import server
from datetime import datetime, date
import pandas as pd
import urllib
import os
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from dateutil.relativedelta import *

server.include_df_index = True

def download_data(obl_index):
    url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&province_id={}&year1=1998&year2=2022&type=Mean".format(obl_index)
    wp = urllib.request.urlopen(url)
    text = wp.read()
    now = datetime.now()
    date_and_time = now.strftime("%d_%m_%Y_%H:%M:%S")
    with open(f"data/NOAA_ID_{obl_index}_{date_and_time}.csv", "wb") as file:
        file.write(text)

def clear_string(string):
    unallowed_characters = "._!*?<>tpre"
    for character in unallowed_characters:
        string = string.replace(character, "")
    return string
    

def change_area_index(old_index, old_to_new):
    return old_to_new[old_index]

cities = ['Vinnytsa', 'Volyn', 'Dnipropetrovsk', 'Donetsk', 'Zhytomyr', 'Zakarpattya', 'Zaporizhya', 
             'Ivano-Frankivsk', 'Kyiv', 'Kirovograd', 'Lugansk', 'Lviv', 'Mykolayiv', 'Odessa', 'Poltava', 'Rivne', 
             'Sumy', 'Ternopil', 'Kharkiv', 'Kherson', 'Khmelnytsy', 'Cherkasy',
             'Chernivtsy', 'Chernigiv', 'Crimea']

def change_data_format(df):
    df["Year"] = pd.to_numeric(df["Year"])
    df["Week"] = pd.to_numeric(df["Week"])
    return df


def city_by_area(area_num, cities):
    return cities[int(area_num) - 1]

def add_dataframe(path_to_dir):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'area']
    old_to_new = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 
                 10: 21, 11: 9, 12: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14,
                 18: 15, 19: 16, 20: 25, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 
                 26: 7, 27: 5}
    dataframes = []
    files = os.listdir(path_to_dir)
    for filename in files:
        file = os.path.join(path_to_dir, filename)
        df = pd.read_csv(file, header = 1, names = headers)
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df[df['Week'].notna()]
        df['Year'] = df['Year'].apply(lambda x: clear_string(x))
        df['area'] = file.split('_')[2]
        df['area'] = df['area'].apply(lambda x: change_area_index(int(x), old_to_new))
        df['area'] = df['area'].apply(lambda x: city_by_area(x, cities))
        dataframes.append(df)
    result = pd.concat(dataframes, axis=0, ignore_index=True)
    return result




class StockExample(server.App):
    title = "NOAA data vizualization"
    global cities
    inputs = [{
        "type": 'dropdown',
        "label": 'NOAA data dropdown',
        "options": [
            {"label": "VCI", "value": "VCI"},
            {"label": "TCI", "value": "TCI"},
            {"label": "VHI", "value": "VHI"}],
        "key": 'ticker',
        "action_id": "update_data"
    },
    
    dict( type="dropdown",
    key="region",
    label="Region",
    options=[{"label":city_by_area(i, cities), "value":city_by_area(i, cities)} for i in range(1, len(cities) + 1)]),


    dict( type="text",
    key="week",
    label="Weeks"),


    dict( type='text',
    key="year",
    label='Year')]

    tabs = ["Plot", "Table"]

    outputs = [
        {
            "type": "plot",
            "id": "plot_sine_wave",
            "control_id":"update_data",
            "on_page_load": False,
            "tab": "Plot"},
        {
            "type": "table",
            "id": "table_id",
            "control_id": "update_data",
            "tab": "Table",
            "on_page_load": False
        }
    ]

    controls = [{
        "type":"button",
        "id":"update_data",
        "label":"refresh the page"
    }]
        
    def getData(self, params):
        df = add_dataframe('./data')
        for i in range(32422, 33669):
            df.drop(i, inplace=True)
        df = df[(df['area'] == params['region']) & 
        (df['Year'].astype('int64') == int(params['year'])) &
        (df['Week'] >= int(params['week'].split('-')[0])) &
        (df['Week'] <= int(params['week'].split('-')[1]))]
        return df  


    def getPlot(self, params):
        df = add_dataframe('./data')
        for i in range(32422, 33669):
            df.drop(i, inplace=True)
        df = self.getData(params)
        df = change_data_format(df)
        df = df.set_index('Week')
        plt.obj = df.plot(y=params['ticker'], grid='True')
        plt.obj.set_ylabel(params['ticker'])
        plt.obj.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.obj.legend([str(params['region'])])
        plt.obj.set_title(f"{params['ticker']} index for {params['week']} weeks {params['year']} year")
        fig = plt.obj.get_figure()
        return fig



app = StockExample()
app.launch(port=9093)