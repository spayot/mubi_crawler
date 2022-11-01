from dataclasses import dataclass, field
from typing import Any

import requests

METACRITIC_URL = "https://www.metacritic.com/autosearch"

_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "47",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.metacritic.com",
    "Origin": "https://www.metacritic.com",
    "Referer": "https://www.metacritic.com/search/all/alice%20and%20the%20mayor/results",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
}


def call_metacritic(title: str) -> dict:
    """call metacritic autosearch to extract meta score through a search by title."""

    resp = requests.post(
        url=METACRITIC_URL,
        data={"search_term": title, "image_size": "98", "search_each": "true"},
        headers=_HEADERS,
    )

    return resp


@dataclass
class MetaCriticMovie:
    url: str = field(repr=False)
    name: str
    meta_score: int
    ref_type: str

    @classmethod
    def from_dict(cls, obj: dict[str, Any]):
        """parse objects from API response to extract relevant data."""
        return cls(
            url=obj["url"],
            name=obj["name"],
            meta_score=obj["metaScore"],
            ref_type=obj["refType"],
        )

    @classmethod
    def from_title(cls, title: str):
        """Executes a call to metacritic autosearch and search by title.capitalize
        retrieves product details for first result returned (if any).
        If no match was found, returns None"""
        resp = call_metacritic(title.lower())
        if resp.status_code == 200:
            results = resp.json()["autoComplete"]["results"]
            for result in results:
                # filtering out non-movie results
                if result["refType"] == "Movie":
                    return cls.from_dict(result)

            print(f"\tMetacritic: No results found for title: {title}")
            return None

        print(
            f"\tError querying metacritic API with {title}. status code: {resp.status_code}"
        )
