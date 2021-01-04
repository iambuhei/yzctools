import cv2
import requests
import os
import pandas as pd
import numpy as np
import matchanalysis


def ava_dl(uid: str):

    print(f"downloading ava_{uid}.jpg")
    res = requests.get(f'http://a.ppy.sh/{uid}').content
    with open(f'data/avatar_{uid}.jpg', 'wb') as f:
        f.write(res)


def ava_img(uid: str):

    img_path = f'data/avatar_{uid}.jpg'
    if not os.path.isfile(img_path):
        ava_dl(uid)
    img = cv2.imread(img_path)

    return img


def gen_img(sdf: pd.DataFrame, size: int = 128):

    count_user = sdf.shape[0]
    img = np.zeros((size * 2, size * count_user, 3), dtype='uint8')

    for i in range(count_user):
        uid = sdf['uid'][i]

        avatar = cv2.resize(ava_img(uid), (size, size))
        img[:size, i * size:(i + 1) * size] = avatar.copy()

        username = matchanalysis.get_username(uid)
        username_img = gen_text_img(str(username), size, 6 / len(username), 1)
        img[size:int(3 * size / 2), i * size:(i + 1) * size] = username_img.copy()

        score = int(sdf['scoring'][i])
        score_img = gen_text_img(str(score), size, 2, 4)
        img[int(3 * size / 2):, i * size:(i + 1) * size] = score_img.copy()

    return img


def gen_text_img(text: str, size: int = 128, font_scale: float = 2, thickness: int = 2):

    img = np.zeros((int(size / 2), size, 3), dtype='uint8')
    img[:] = 255
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font_face, font_scale, thickness)
    origin = (int(size / 2 - text_size[0][0] / 2), int(size / 4 + text_size[0][1] / 2))

    cv2.putText(img, text, origin, font_face, font_scale, (0, 0, 0), thickness)

    return img


def test():

    match = matchanalysis.Match('67178685', count_warmup=2)
    print(match)
    img_out = gen_img(match.scored_match_df([10, 6, 3, 1]), size=128)
    cv2.imwrite('result.jpg', img_out)
    cv2.imshow('res', img_out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test()
