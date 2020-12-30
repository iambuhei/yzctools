from const import API_URL, API_KEY
from requests import get, Response
import pandas as pd
from typing import List, Optional


class Score(object):

    uid: str
    score: int
    acc: float

    def __init__(self, score_dict: dict):
        self.uid = score_dict['user_id']
        self.score = int(score_dict['score'])
        self.acc = acc(score_dict)

    def __lt__(self, other):
        return self.acc < other.acc or (self.score < other.score and self.acc == other.acc)

    def __eq__(self, other):
        return self.acc == other.acc and self.score == other.score

    def __str__(self):
        return str({'uid': self.uid, 'score': self.score, 'acc': self.acc})
    __repr__ = __str__


class Game(object):

    gid: str
    bid: str
    finished: bool
    scores: List[Score]

    def __init__(self, game_dict: dict, rm_zeros: bool = True):
        self.gid = game_dict['game_id']
        self.bid = game_dict['beatmap_id']
        self.finished = bool(game_dict['end_time'])
        self.scores = analyze_scores(game_dict['scores'], rm_zeros)

    def scores_df(self) -> pd.DataFrame:
        res_df = pd.DataFrame(columns=('uid', 'score', 'acc'))
        res_df['uid'] = pd.Series([s.uid for s in self.scores], dtype=object)
        res_df['score'] = pd.Series([s.score for s in self.scores], dtype=int)
        res_df['acc'] = pd.Series([s.acc for s in self.scores], dtype=float)
        return res_df

    def rank_df(self) -> pd.DataFrame:
        res_df = pd.DataFrame(columns=('uid', f'game_{self.gid}'))
        res_df['uid'] = pd.Series([s.uid for s in self.scores], dtype=object)
        rank_list = list(range(1, len(self.scores) + 1))

        for i in range(1, len(self.scores)):
            if self.scores[i] == self.scores[i - 1]:
                rank_list[i] = rank_list[i - 1]

        res_df[f'game_{self.gid}'] = pd.Series(rank_list, dtype=int)
        return res_df

    def __str__(self):
        return f'Game(gid={self.gid}, bid={self.bid}, scores={self.scores})'
    __repr__ = __str__


class Match(object):

    mid: str
    res: Response
    games: List[Game]
    match_df: pd.DataFrame

    def __init__(self, match_url: str, count_warmup: int = 2):
        self.mid = ''.join(list(filter(str.isdigit, match_url)))
        self.res = get(API_URL + f"/get_match?k={API_KEY}&mp={self.mid}")
        self.games = []
        self.match_df = pd.DataFrame()

        if is_valid(self.res):

            bid_unique = set()
            for game_dict in reversed(self.res.json()['games'][count_warmup:]):
                game = Game(game_dict, rm_zeros=True)
                if game.finished and game.bid not in bid_unique:
                    bid_unique.add(game.bid)
                    self.games.append(game)
            self.games.reverse()

            self.match_df = analyze_match(self.games)

    def scored_match_df(self, scoring_list: Optional[List[int]] = None) -> pd.DataFrame:
        res_df = self.match_df.copy()
        if scoring_list:
            for i, s in enumerate([0] + scoring_list):
                res_df.replace(i, s, inplace=True)

        res_df['scoring'] = res_df.drop(['uid'], axis=1).aggregate(sum, axis=1)
        return res_df

    def __str__(self):
        return str(self.match_df)
    __repr__ = __str__


def acc(score_dict: dict) -> float:

    count_300 = int(score_dict['count300'])
    count_100 = int(score_dict['count100'])
    count_50 = int(score_dict['count50'])
    count_miss = int(score_dict['countmiss'])

    count = count_300 + count_100 + count_50 + count_miss
    acc_loss = (count_miss + 5 / 6 * count_50 + 2 / 3 * count_100) / count
    acc_raw = 1 - acc_loss

    return int(acc_raw * 10000) / 100


def analyze_scores(scores_list: dict, rm_zeros: bool = True) -> List[Score]:

    res_list = []

    for score_dict in scores_list:
        res_list.append(Score(score_dict))

    if rm_zeros:
        res_list = filter(lambda s: getattr(s, 'acc') > 0.05, res_list)

    return sorted(res_list, reverse=True)


def is_valid(res: Response) -> bool:
    return res.status_code == 200 and res.json()['match']


def analyze_match(games: List[Game]) -> pd.DataFrame:

    match_df = pd.DataFrame(columns=('uid',))

    for game in games:
        game_df = game.rank_df()
        match_df = pd.merge(match_df, game_df, how='outer', on='uid')

    return match_df.fillna(0)


def get_username(uid: str) -> str:
    res = get(API_URL + f"/get_user?k={API_KEY}&u={uid}")
    return res.json()[0]['username']
