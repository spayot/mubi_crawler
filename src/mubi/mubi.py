import os
from dataclasses import dataclass, field
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from typing import Union

import pandas as pd
import requests

from .metacritic import MetaCriticMovie

MUBI_FILM_GROUP_URL = "https://api.mubi.com/v3/film_groups?size=40&offset=0"
MUBI_FILM_GROUP_ITEMS_URL = "https://api.mubi.com/v3/film_groups/{id}/film_group_items"

_HEADERS = {
    "ANONYMOUS_USER_ID": "5117ffd6-467c-421a-ae38-b3eb93a4df01",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "CLIENT": "web",
    "Client-Accept-Video-Codecs": "h265,vp9,h264",
    "Client-Country": "US",
    "Connection": "keep-alive",
    "Host": "api.mubi.com",
    "If-None-Match": 'W/"91f7e35ef49aa19663944255992cd638"',
    "Origin": "https://mubi.com",
    "Referer": "https://mubi.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
}

POOL_SIZE = 4


@dataclass
class MubiMovie:
    title: str
    duration: int
    year: int = field(repr=False)
    web_url: str = field(repr=False)
    critic_review_rating: float = field(repr=False)
    director: str = field(repr=False)
    genres: list[str] = field(default_factory=list)
    historic_countries: list[str] = field(default_factory=list, repr=False)
    meta_score: int = field(default=None)

    def __post_init__(self):
        meta_critic = MetaCriticMovie.from_title(self.title)
        if meta_critic:
            self.meta_score = meta_critic.meta_score

    @classmethod
    def from_dict(cls, obj: dict):
        obj = obj["film"]
        return cls(
            title=obj.get("title"),
            duration=obj.get("duration"),
            year=obj.get("year"),
            web_url=obj.get("web_url"),
            genres=obj.get("genres"),
            critic_review_rating=obj.get("critic_review_rating"),
            historic_countries=obj.get("historic_countries"),
            director=obj.get("directors")[0].get("name"),
        )


@dataclass
class MubiCollection:
    name: str
    id: int
    movies: list[MubiMovie] = field(default_factory=list, repr=False)

    def __len__(self) -> int:
        return len(self.movies)

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(name=obj.get("title"), id=obj.get("id"))

    def get_movies(self) -> None:
        next_page = 1
        while next_page:
            meta, movies = self._get_next_page_of_movie(next_page)
            self.movies += movies
            next_page = meta["next_page"]

    def _get_next_page_of_movie(self, page) -> list[MubiMovie]:

        params = {"include_upcoming": True, "page": page, "per_page": 40}
        # call
        resp = requests.get(
            MUBI_FILM_GROUP_ITEMS_URL.format(id=self.id),
            params=params,
            headers=_HEADERS,
        )

        if resp.status_code == 200:
            films = resp.json()["film_group_items"]
            meta = resp.json()["meta"]
            with Pool(POOL_SIZE) as pool:
                movies = pool.map(MubiMovie.from_dict, films)

            return meta, movies

    def to_frame(self) -> pd.DataFrame:
        df = pd.DataFrame([movie.__dict__ for movie in self.movies])
        return df.sort_values("meta_score", ascending=False)

    def save(self, datapath: Union[Path, str] = None) -> None:
        """by default stores in a folder named after the date."""

        if type(datapath) == str:
            datapath = Path(datapath)

        today_path = datapath / _get_today_to_str()

        if not os.path.exists(today_path):
            os.mkdir(today_path)

        filename = self.name.lower().replace(" ", "_") + ".csv"

        self.to_frame().to_csv(today_path / filename, index=False)


def _get_today_to_str() -> str:
    return datetime.today().strftime("%Y%m%d")


@dataclass
class MubiAllFilmGroups:
    extraction_date: str = field(default_factory=_get_today_to_str)
    collections: list[MubiCollection] = field(default_factory=list, repr=False)

    def extract_groups(self):
        """call MUBI film group API and extract list of collections to crawl from"""
        resp = requests.get(MUBI_FILM_GROUP_URL, headers=_HEADERS)
        if resp.status_code == 200:
            self.collections = [MubiCollection.from_dict(obj) for obj in resp.json()]

    def crawl_all_collections(self, datapath: Path):
        """Collects movie data from each collections."""
        for collection in self.collections:
            print(f"\nstarted crawling of {collection}")
            collection.get_movies()
            collection.save(datapath)
            print(f"\n completed crawling of {collection}")

    def consolidate_all_films(self, datapath: Path):
        dfs = [
            pd.read_csv(file)
            for file in (datapath / self.extraction_date).glob("*.csv")
        ]

        df = (
            pd.concat(dfs)
            .drop_duplicates(subset=["title", "year"])
            .sort_values("meta_score", ascending=False)
        )

        df.to_csv(datapath / f"{self.extraction_date}_mubi.csv")
