import os
import re
import pandas as pd
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(
    client_id=os.environ['SPOTIPY_CLIENT_ID'],
    client_secret=os.environ['SPOTIPY_CLIENT_SECRET']
)

sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager
)

def find_band_spotify(band_name):
    """
    For a given band name, find Spotify profile
    """
    results = sp.search(q='artist:' + band_name, type='artist')
    items = results['artists']['items']
    return items


def get_thai_bands():
    """
    Return all Thai bands from Wikipedia page
    """
    band_urls = []
    artists_url = (
        "https://th.wikipedia.org/wiki/%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%8A%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%81%E0%B8%A5%E0%B8%B8%E0%B9%88%E0%B8%A1%E0%B8%94%E0%B8%99%E0%B8%95%E0%B8%A3%E0%B8%B5%E0%B8%AA%E0%B8%B1%E0%B8%8D%E0%B8%8A%E0%B8%B2%E0%B8%95%E0%B8%B4%E0%B9%84%E0%B8%97%E0%B8%A2"
    )
    r = requests.get(artists_url)
    soup = BeautifulSoup(r.content)

    for li in soup.find_all("li")[0:-47]:
        band_urls.append({
            "url": li.find('a').get('href') if li.find('a') is not None else None,
            "band_name": li.text if li.text != "" else None,
        })
    bands_df = pd.DataFrame(band_urls)
    bands_df["band_name_english"] = bands_df.band_name.map(
        lambda s: re.search(r'\((.*?)\)', s).group(1) if re.search(r'\((.*?)\)', s) is not None else ""
    )
    bands_df['band_name_thai'] = [
        r['band_name'].replace("(", "").replace(")", "").replace(r.band_name_english, '')
        for _, r in bands_df.iterrows()
    ]
    bands_df['url']  = bands_df['url'].map(
        lambda x: urljoin("https://th.wikipedia.org/", x) if x.startswith("/wiki/") else ""
    )
    return bands_df

