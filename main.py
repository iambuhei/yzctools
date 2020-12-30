import matchanalysis
import pandas as pd
import img
import cv2
from const import PATH_CSV_SAVE
from fastapi import FastAPI
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()


@app.post('/')
async def get_score_dataframe(match_url: str, count_warmup: int = 2,
                              scoring_list: List[int] = (10, 6, 3, 1)):

    match = matchanalysis.Match(match_url, count_warmup)
    sdf = match.scored_match_df(scoring_list)
    sdf = pd.Series(sdf['scoring'].array, index=sdf['uid'])
    sdf.to_csv(PATH_CSV_SAVE)

    return sdf


@app.post('/img')
async def get_score_img(match_url: str, count_warmup: int = 2,
                        scoring_list: List[int] = (10, 6, 3, 1)):

    match = matchanalysis.Match(match_url, count_warmup)
    sdf = match.scored_match_df(scoring_list)
    img_out = img.gen_img(sdf, size=128)
    cv2.imwrite('result.jpg', img_out)
    sdf.to_csv(PATH_CSV_SAVE)

    return FileResponse('result.jpg')


def test():

    match = matchanalysis.Match("https://osu.ppy.sh/community/matches/54424215", count_warmup=2)
    sdf = match.scored_match_df([10, 6, 3, 1])
    sdf = pd.merge(pd.Series(sdf['uid'].apply(matchanalysis.get_username), name='username'), sdf,
                   left_index=True, right_index=True, how='outer')
    sdf.to_csv(PATH_CSV_SAVE)
    print(sdf[['username', 'scoring']])


if __name__ == '__main__':
    test()
