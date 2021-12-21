'''This scrapes recipes from https://www.giallozafferano.com'''

import requests
import re
import os
import numpy as np
import pandas as pd
import csv
from bs4 import BeautifulSoup


URL = 'https://www.giallozafferano.com/'

COURSES_URL = [
    "latest-recipes/",
    "recipes-list/Appetizers/",
    "recipes-list/First-Courses/",
    "recipes-list/Main-Courses/",
    "recipes-list/Sweets-and-Desserts/"
    "recipe_list/Leavened-products/"
]

def get_hrefs_per_page(response):
    ''' 
    args:
        response_text <- datatype STRING with html code of a web page.

    returns:
        LIST of urls to linked web pages.
    '''
    # Getting the body of the html content
    main_corpus = BeautifulSoup(response, "html.parser").body.main.div 

    # Extracting the desired urls and return a list with cleaned duplicates
    urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.][html]+', str(main_corpus))
    return list(dict.fromkeys(urls))


def get_recipe_hrefs(courses_url, url=URL):
    ''' 
    args:
        main url <- datatype STRING with the url of the web page e.g. 'https://www.giallozafferano.com/'.
        courses_url <- datatype STRING; item from the globally defined COURSES_URL list.
    
    returns:
        url_list <- datatype LIST; with the entire urls as strings for each recipe.
    '''
    lst_measure = 0
    url_list = ['']
    counter = 1
    while len(url_list) > lst_measure :
        # Considering that in the first run, the url appendix "page" is not part of the url
        if counter == 1:
            url_list = []
            response = requests.get(URL + os.sep + courses_url)
        else:   response = requests.get(URL + os.sep + courses_url + os.sep + f'page{counter}')

        lst_measure = len(url_list)
        url_list += get_hrefs_per_page(response.text)
        counter += 1

    return url_list


def get_meta_data(df, url=URL):
    ''' 
    args:
        df <- DataFrame with all the urls for the recipe pageTimes
    
    returns:
        output <- List with the meta data
    '''
    output = []
    for i in range(len(df)):
        url = df.iloc[i][0] # Get URL of ith recipe in the dataframe #<====####### something is hard coded HERE ###########
        response = requests.get(url)
        zallo_soup = BeautifulSoup(response.text, "html.parser") # Get all recipe text
        html_part = zallo_soup.body.find_all("span", {"class": "gz-name-featured-data"}) # Get all html line with header information
        
        meta_lst = []
        for k in range(len(html_part)-1):
            meta_lst.append((re.findall(r'>(.*?):', str(html_part[k]))[0] ,re.findall(r'<strong>(.*?)</strong>', str(html_part[k]))[0]))
            
        output.append(meta_lst)
    return output


def get_ingredients(df, url=URL):
    '''
    args:
        df <- DataFrame with all the urls for the recipe pageTimes
    
    returns:
        ingr_lst <- List with the meta data
    '''
    ingr_lst = []
    for i in range(len(df)):
        url = df.iloc[i][0] #<====####### something is hard coded HERE ###########
        response = requests.get(url)
        zallo_soup = BeautifulSoup(response.text, "html.parser")

        ingredients = str(zallo_soup.body.find_all("dd", {"class": "gz-ingredient"}))

        ingr_lst.append(re.findall(r'>(.*?)</a>', ingredients))
    
    return ingr_lst 


CLEANR = re.compile('<.*?>') 
def cleanhtml(raw_html):
    ''' 
    Little helper function to remove all inside <...>
    '''
    raw = raw_html.replace('<span class="num-step">', '#')
    cleantext = re.sub(CLEANR, '', raw)
    return cleantext


def get_title(url):
    ''' This extracts the dish title form the url
    '''
    return re.findall('recipes/(.*?).html', url)[0]


def get_cooking_instructions(df, url=URL):
    '''
    args:
        df <- DataFrame with all the urls for the recipe pageTimes
    
    returns:
        prep_list <- List with Dictionaries with keys as chronological step number and values as instrction text
    '''
    prep_list = []
    for i in range(len(df)):
        url = df.iloc[i][0]  #<====####### something is hard coded HERE ###########
        response = requests.get(url)
        zallo_soup = BeautifulSoup(response.text, "html.parser")

        # Get the html part with the cooking instruction text
        steps = zallo_soup.body.find_all("div", {"class": "gz-content-recipe-step"})

        # Get the clean instruction text of the web page
        output = cleanhtml(str(steps)).strip("[]").replace('\n', '')
        try:
            values = [x for x in re.split('(#\d+)', output) if x[0] != '#']
            keys = np.linspace(0, len(values), num = len(values)+1, dtype = int).tolist()
        except:
            values = ['nothing found']
            keys = [0]

        prep_list.append(dict(zip(keys, values)))

    return prep_list


def meta_to_dict(df_column):
    lst = re.findall(r"'(.*?)'", df_column)    
    keys = []
    values =[]
    for i, item in enumerate(lst):
        if i%2 == 0:
            keys.append(item)
        else:    values.append(item)

    return dict(zip(keys, values))



def main():
    '''
    This contains code to be executed
    '''
    recipe_lst = []
    for course_url in COURSES_URL:
        recipe_lst += get_recipe_hrefs(course_url)
    
    recipe_lst = list(set(recipe_lst))

    print(f'Number of found urls for recipes: {len(recipe_lst)}')

    # Create dataframe from recipe urls
    df = pd.DataFrame({'url': recipe_lst})

    df['meta'] = get_meta_data(df)
    print(f'Number of created meta infromations: {len(df.meta)}')

    df['ingredients'] = get_ingredients(df)
    print(f'Number of created ingredients lists: {len(df.ingredients)}')

    df['instruction_dict'] = get_cooking_instructions(df)
    print(f'Number of created dictionaries from instruction text: {len(df.instruction_dict)}')
    df.to_csv('recipes_pre.csv')

    df['title'] = df['url'].apply(get_title)

    df_meta = []
    for i in range(len(df)):
        df_meta.append(meta_to_dict(df.meta[i]))
    df.meta = df_meta

    df.to_csv('recipe_list.csv')
    
if __name__ == '__main__':
    main()
