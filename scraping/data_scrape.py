from .liquor.scrape_liquor import make_soup, get_sub_urls, get_all_cocktails_in_url
from .postgres import create_connection

def scrape_cocktails(sites, connection, table_name):
    list_of_sites = sites.split(',')
    for site in list_of_sites:
        if site == 'https://www.liquor.com/':
            website = make_soup(site)
            cocktail_type = website.find('nav',class_='comp l-container fullscreen-nav',role='navigation').find('ul',class_='fullscreen-nav__list').find_all('a',class_='fullscreen-nav__list-item-link')[0].get('href')
            cocktails_by = get_sub_urls(cocktail_type)
            cocktails_by.remove('https://www.liquor.com/other-recipes-4779379')
            for url in cocktails_by:
                get_all_cocktails_in_url(url, connection, table_name)
                sub_urls = get_sub_urls(url)
                for sub_url in sub_urls:
                    get_all_cocktails_in_url(sub_url, connection, table_name)

    connection.close()
