from typing import Tuple
import requests
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from tqdm import tqdm

from util import text_array_for_row

from flask import Request
import functions_framework
from google.cloud import storage


def get_bucket():

    storage_client = storage.Client()
    bucket_name = "utveksling-stats-bucket"
    bucket = storage_client.get_bucket(bucket_name)

    return bucket


@functions_framework.http
def main(r: Request) -> Tuple[str, int, dict]:
    if r.path.startswith("/stats"):
        return stats(r)
    elif r.path.startswith("/update"):
        return update_stats(r), 200, {}
    else:
        return "Not found", 404, {}


def stats(request: Request) -> Tuple[str, int, dict]:
    program = request.args.get("search")

    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    bucket = get_bucket()

    pickle_str = bucket.blob("data.pickle").download_as_string()
    stats: pd.DataFrame = pickle.loads(pickle_str)

    if program is not None:
        stats = stats[stats["Studieprogram"].str.contains(f"(?i){program}")]

    countries = stats["Country_en"].value_counts()
    response = countries.to_dict()

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}

    return json.dumps(response), 200, headers


# Call this function whenever we update the daata
# Typically we would do this once a year
def update_stats(event):
    bucket = get_bucket()

    countries_blob = bucket.blob("countries.pickle")
    data_blob = bucket.blob("data.pickle")

    countries_blob.download_to_filename("countries.pickle")

    countries = pickle.load(open("countries.pickle", "rb"))

    # Update the stats and write them to google storage
    BASE_URL = "https://www.ntnu.no/studier/studier_i_utlandet/rapport/table.php"
    payload = {
        "away_country": "default",
        "away_city": "",
        "away_university": "",
        "home_university": "default",
        "searchOldReports": "yes",
        "home_faculty": "",
        "home_institute": "",
        "exchange_program": "default",
        "exchange_period": "default",
        "number-of-views": "1163",
        "advanced_search_enabled": "yes",
        "language": "no",
    }
    print("Fetching NTNU data")
    data = requests.get(BASE_URL, params=payload)
    soup = BeautifulSoup(data.content.decode("utf8"), "html.parser")
    rows = soup.find_all("tr")

    df = pd.DataFrame(
        list(map(lambda x: text_array_for_row(x), rows[1:])),
        columns=text_array_for_row(rows[0]),
    )
    df = df.dropna()

    countries = df["Land"].unique()
    countries_en = {}

    # We want to translate all the country names into English for the site
    translator = GoogleTranslator(source="no", target="en")
    print("Translating country names")
    for country in tqdm(countries):
        en_country = translator.translate(country)
        countries_en[country] = en_country

    df["Country_en"] = df["Land"].map(countries_en)
    df.loc[df["Land"] == "USA", "Country_en"] = "United States of America"
    df.loc[df["Land"] == "Korea", "Country_en"] = "South Korea"

    df.to_pickle("data.pickle")
    data_blob.upload_from_filename("data.pickle")

    return "Ok!"
