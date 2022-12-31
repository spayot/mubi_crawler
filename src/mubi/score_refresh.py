import logging
import time

import pandas as pd

from .metacritic import MetaCriticMovie

LOGDIR = "../logs/mubi.log"
LOGFREQ = 10
DATAPATH = "../data/20221208_mubi.csv"


logging.basicConfig(
    filename=LOGDIR,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


def recall_metacritic(datapath: str, timesleep: float = 0.5):
    movies = pd.read_csv(datapath)
    movies_to_rescore = get_movies_to_rescore(movies)
    new_scores = get_metascores(movies_to_rescore, timesleep)
    movies.loc[new_scores.index, "meta_score"] = new_scores
    movies.sort_values("meta_score", ascending=False)
    movies.to_csv(datapath)


def get_movies_to_rescore(movies: pd.DataFrame) -> pd.DataFrame:
    is_without_score = movies.meta_score.isnull() | movies.meta_score == -1
    return movies[is_without_score]


def get_metascores(movies_without_score: pd.DataFrame, timesleep: float) -> pd.Series:
    meta_scores = {}
    start_msg = f"MetaCritic Recall: Started with {len(movies_without_score):,} movies without score"
    logging.info(start_msg)

    tried_count, successful_count = 0, 0

    for row_id, row in movies_without_score.iterrows():
        mcm = MetaCriticMovie.from_title(title=row.title, year=row.year)
        tried_count += 1
        if mcm:
            meta_scores[row_id] = mcm.meta_score
            successful_count += 1

        time.sleep(timesleep)

        if tried_count % LOGFREQ == 0:
            logging.info(
                f"MetaCritic Recall: {successful_count:>5,} / {tried_count:>5,} scores extracted"
            )

    print(meta_scores)
    return pd.Series(meta_scores)


recall_metacritic(DATAPATH)
