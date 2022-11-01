from pathlib import Path

from src.mubi import mubi

DATAPATH = "data/"


def main(path: str):
    path = Path(path)
    app = mubi.MubiAllFilmGroups()
    # identify top 40 collections in now_showing section
    app.extract_groups()

    # crawl all films from each collection and save in a folder (generated based on current date)
    app.crawl_all_collections(path)

    # consolidate into single csv
    app.consolidate_all_films(path)

    print(f"All files saved in data/{mubi._get_today_to_str()} folder")


if __name__ == "__main__":
    main(DATAPATH)
