import argparse
import json
from scraping.postgres import create_connection, create_database, create_table
from scraping.data_scrape import scrape_cocktails

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--config_file',  type=str, default='db_config.json')
    parser.add_argument('-s','--sites', type=str, default='https://www.liquor.com/')
    args = parser.parse_args()

    with open(args.config_file) as json_file:
        config = json.load(json_file)

    conn = create_connection(config)
    args = parser.parse_args()
    
    create_database(config['dbName'], conn)
    create_table(config['tableName'], conn)
    scrape_cocktails(args.sites, conn, config['tableName'])
    conn.close()