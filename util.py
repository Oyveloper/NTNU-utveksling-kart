import requests
from dotenv import load_dotenv
import os

load_dotenv()

def text_array_for_row(row):
    res = []
    for el in row.children:
        if el != '\n':
            res.append(el.text)
    return res

def search_country(query: str) -> str:
    payload = {
        'access_key': os.getenv("ACCESS_KEY"),
        'query': query,
    }
    data = requests.get("http://api.positionstack.com/v1/forward", params = payload)
    j = data.json()
    if 'data' not in j:
        print(f"Could not find: {query}")
        return "Unknown"

    if len(j['data']) == 0:
        print(f"Could not find: {query}")
        return "Unknown"
    try:
        return j['data'][0]['country']
    except:
        return "Unknown"
