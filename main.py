import requests
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from tqdm import tqdm

from util import text_array_for_row, search_country

from flask import request, jsonify
import functions_framework
from google.cloud import storage

def get_bucket():

    storage_client = storage.Client()
    bucket_name = "utveksling-stats-bucket"
    bucket = storage_client.get_bucket(bucket_name)

    return bucket


@functions_framework.http
def stats(request: request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    bucket = get_bucket()

    bucket.blob("data.pickle").download_to_filename("data.pickle")
    bucket.blob("countries.pickle").download_to_filename("countries.pickle")
    bucket.blob("country_counts.pickle").download_to_filename("country_counts.pickle")
    stats: pd.DataFrame = pickle.load(open("data.pickle", "rb"))
    countries: pd.DataFrame = pickle.load(open("country_counts.pickle", "rb"))


    response = {
        "countries": countries.to_dict()
    }

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

    return json.dumps(response), 200, headers


# Call this function whenever we update the daata
# Typically we would do this once a year
def update_stats(event):
    bucket = get_bucket()

    countries_blob = bucket.blob("countries.pickle")
    data_blob = bucket.blob("data.pickle")
    country_count_blob = bucket.blob("country_counts.pickle")
    country_count_json_blob = bucket.blob("country_counts.json")

    countries_blob.download_to_filename("countries.pickle")

    countries = pickle.load(open("countries.pickle", "rb"))


    # Update the stats and write them to google storage
    BASE_URL = "https://www.ntnu.no/studier/studier_i_utlandet/rapport/table.php"
    payload = {
        'away_country':'default',
        'away_city': '',
        'away_university': '',
        'home_university':'default',
        'searchOldReports':'yes',
        'home_faculty':'',
        'home_institute': '',
        'exchange_program':'default',
        'exchange_period':'default',
        'number-of-views':'1000',
        'advanced_search_enabled':'yes',
        'language':'no'
    }
    print("Fetching NTNU data")
    data = requests.get(BASE_URL, params = payload)
    soup = BeautifulSoup(data.content.decode("utf8"), 'html.parser')
    rows = soup.find_all("tr")

    df = pd.DataFrame(list(map(lambda x: text_array_for_row(x), rows[1:])), columns=text_array_for_row(rows[0]))
    df = df.dropna()

    print("Starting loop of cities to find all countries")
    # Find all the cities from the data
    cities = df['By'].unique()
    for city in tqdm(cities):
        if not city in countries:
            countries[city] = search_country(city)


    df['Land'] = df.apply(lambda x: countries[x['By']], axis=1)
    counties_pickle = pickle.dumps(countries)
    countries_blob.upload_from_string(counties_pickle)

    # We want to translate all the country names into Norwegian for the site
    # translator = GoogleTranslator(source='auto', target='no')
    # for city, country in countries.items():
        # break
        # if country is not None:
            # countries[city] = translator.translate(country)

    df.loc[df['Land'] == "United States", 'Land'] = 'United States of America'
    df.to_pickle('data.pickle')
    data_blob.upload_from_filename('data.pickle')

    # Country counts
    country_count = df['Land'].value_counts()

    country_count.to_pickle('country_counts.pickle')
    country_count_blob.upload_from_filename('country_counts.pickle')
    country_count_json_blob.upload_from_string(country_count.to_json())

    return "hello world"

