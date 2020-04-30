from bs4 import BeautifulSoup
import requests
import numpy as np
from ..postgres import add_to_database

def make_soup(url):
    '''
    INPUT: url string
    OUTPUT: BeautifulSoup object
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_sub_urls(website):
    '''
    INPUT: url string from liquor.com
    Gathers sub list of links in header and gets the urls of those links
    OUTPUT: list of url strings
    '''
    sub_set = set()
    sub_urls = make_soup(website).find('ul', class_='comp child-indices truncated-list').find_all('a')
    for item in sub_urls:
        sub_set.add(item.get('href'))
    return sub_set

def get_name_and_ingredients(soup_obj):
    '''
    INPUT: Beautiful Soup object for liquor.com
    OUTPUT: Name of the cocktail, ingredients in the cocktail
    '''
    ingredients = set()
    ingredient_list_html = soup_obj.find_all('li',class_='simple-list__item js-checkbox-trigger ingredient')
    for ingredient in ingredient_list_html:
        ingredients.add(ingredient.text.strip('\n'))
    name = soup_obj.find('h1',class_='heading__title').text
    return name, ingredients

def get_rating(soup_obj):
    '''
    INPUT: Beautiful Soup object for liquor.com
    OUTPUT: int/float - Average rating of the cocktail
    '''
    full_star_ratings = soup_obj.find_all('a', class_='active')
    all_stars = set()
    for star in full_star_ratings:
        all_stars.add(int(star.get('data-rating')))
    if len(all_stars) > 0:
        full_star = max(all_stars)
    else:
        full_star = np.nan
    half_stars = soup_obj.find_all('a', class_='half')
    if len(half_stars) > 0:
        full_star += 0.5
    return full_star

def get_description(soup_obj):
    '''
    INPUT: Beautiful Soup object for liquor.com
    OUTPUT: int/float - Average rating of the cocktail
    '''
    description = soup_obj.find('div', class_='comp mntl-sc-block mntl-sc-block-html').text.strip('\n')
    return description

def get_steps(soup_obj):
    '''
    
    '''
    steps_list = soup_obj.find('ol', class_='comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup')
    steps_str = ''
    if len(steps_list) != None:
        steps = steps_list.find_all('li', class_='comp mntl-sc-block-group--LI mntl-sc-block mntl-sc-block-startgroup')
        all_steps = [step.find('p').text for step in steps]
        for part in all_steps:
            steps_str += str(part) + ' '
    return steps_str
    
def preprocess_cocktail(soup_obj):
    '''
    INPUT: Beautiful Soup object for liquor.com
    OUTPUT: name, ingredients, and rating of the cocktail
    '''
    name, ingredient_list = get_name_and_ingredients(soup_obj)
    rating = get_rating(soup_obj)
    if len(ingredient_list) > 0:
        steps = get_steps(soup_obj)
        description = get_description(soup_obj)
    else:
        steps = ''
        description = ''
    # In future plan to save cocktail to database instead of returning
    return name, ingredient_list, rating, steps, description

def get_all_cocktails_in_url(url, connection, table_name):
    '''
    INPUT: liquor.com url to get recipes from
            dictionary to save cocktail information to
    OUTPUT: Does not return anything. Dictionary will be filled with cocktail
            ingredients and rating
    '''
    cocktail_database = set()
    # Get a list of all cocktail objects on the page
    cocktails = make_soup(url).find_all('div',class_='comp card-list__item mntl-block')
    for cocktail in cocktails:
        # if there is no link for that object skip it else get the url
        if cocktail.find('a') == None:
            continue
        else:
            cocktail_url = cocktail.find('a').get('href')
            
        soup_obj = make_soup(cocktail_url)
        name, ingredients, rating, steps, description = preprocess_cocktail(soup_obj)
        # Add cocktail to the dictionary if there ingredients on the page
        if len(ingredients) > 0:
            if name not in cocktail_database:
                cocktail_database.add(name)
                insert_str = f"INSERT INTO {table_name} (‘name’, ‘recipe’, ‘rating’, ‘steps', 'description') VALUES ({name}, {ingredients}, {steps}, {rating}, {description});"
                add_to_database(insert_str, connection)
        else:
            # If there are no ingredients on the page it means that it is a page that has a list of 
            # cocktails that we have to iterate through
            sub_cocktail_obj = make_soup(cocktail_url)
            sub_cocktails = sub_cocktail_obj.find_all('li', class_='comp ordered-list__item mntl-block')
            for sub_cocktail in sub_cocktails:
                links = sub_cocktail.find_all('a')
                for link in links[::-1]:
                    if link.text == 'Get the recipe':
                        sub_soup_obj = make_soup(link.get('href'))
                        sub_name, sub_ingredients, sub_rating, sub_steps, sub_description = preprocess_cocktail(sub_soup_obj)
                        if sub_name not in cocktail_database:
                            cocktail_database.add(sub_name)
                            sub_insert_str = f"INSERT INTO {table_name} (‘name’, ‘recipe’, ‘rating’, ‘steps', 'description) VALUES ({sub_name}, {sub_ingredients}, {sub_steps}, {sub_rating}, {sub_description});"
                            add_to_database(sub_insert_str, connection)
                        break

