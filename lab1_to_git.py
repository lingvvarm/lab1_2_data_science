#!/usr/bin/env python
# coding: utf-8

# Імпорт необхідних бібліотек

# In[1]:


from datetime import datetime
import pandas as pd
import urllib
import os
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# Процедура завантаження файлів з даними

# In[2]:


def download_data(obl_index):
    url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&province_id={}&year1=1998&year2=2022&type=Mean".format(obl_index)
    wp = urllib.request.urlopen(url)
    text = wp.read()
    now = datetime.now()
    date_and_time = now.strftime("%d_%m_%Y_%H:%M:%S")
    with open(f"data/NOAA_ID_{obl_index}_{date_and_time}.csv", "wb") as file:
        file.write(text)


# Завантажуємо дані по всім областям за допомогою циклу

# In[ ]:


for i in range(1, 28):
    download_data(i)


# Функція для прибирання зайвих символів

# In[3]:


def clear_string(string):
    unallowed_characters = "._!*?<>tpre"
    for character in unallowed_characters:
        string = string.replace(character, "")
    return string


# Функція для зміни індексів на запропоноані у лабораторній роботі

# In[4]:


def change_area_index(old_index, old_to_new):
    return old_to_new[old_index]


# Функція для підставлення назв областей за їх індексами у датафреймі

# In[5]:


cities = ['Vinnytsa', 'Volyn', 'Dnipropetrovsk', 'Donetsk', 'Zhytomyr', 'Zakarpattya', 'Zaporizhya', 
             'Ivano-Frankivsk', 'Kyiv', 'Kirovograd', 'Lugansk', 'Lviv', 'Mykolayiv', 'Odessa', 'Poltava', 'Rivne', 
             'Sumy', 'Ternopil', 'Kharkiv', 'Kherson', 'Khmelnytsy', 'Cherkasy',
             'Chernivtsy', 'Chernigiv', 'Crimea']


# In[6]:


def city_by_area(area_num, cities):
    return cities[int(area_num) - 1]


# Створюємо датафрейм з наших даних

# In[7]:


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


# In[8]:


df = add_dataframe("./data")
df.to_csv('my_data.csv', index=False)
df.head()


# Формуємо вибірку даних

# In[12]:


index = 'Chernigiv'
year = '2022'
VHI = df[(df["area"] == index) & (df["Year"] == year)]['VHI']
print(VHI, "\n", VHI.max(), VHI.min())

