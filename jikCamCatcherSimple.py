import re
import requests
from bs4 import BeautifulSoup
from redis import StrictRedis, ConnectionPool


def get_urls(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print('request error code:', response.status_code)
    except Exception as e:
        print(e)
        return None


def parse(input, cutLetter):
    re_tag = re.compile('</?\w+[^>]*>')
    content = re_tag.sub('', str(input))
    if cutLetter:
        re_useless = re.compile('[a-zA-Z,]')
        return re_useless.sub('', content)
    return content


def getRedisConnectionPool():
    url = 'redis://@localhost:6379/0'
    pool = ConnectionPool.from_url(url)
    return pool


def main():
    headers = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    }

    url_co_prefix = 'https://www.youtube.com/watch?v='

    url_ids = {
        'hitomi': [
            'MwEU_09TaLs','nXjKqkAJ-R8','4lZx2f-TbY0','rftFz2tUbKE','VFgpwfEIrnI',
            'u-GRWRs_d6I','yQFzeBzO_ZE','zfaGTwmxG3A','kMYEntl-_js','mVH_dzY3wRI',
            'IH7cIEByWWU','t_LcpM-QG-4','0hr-DyTWLU4','9eIfStw-e_c','1r6fPvCt1UE',
            'XCZEnJ5L81Q','KScSFIrl8HQ','txH9eX8hD_Y','bxWD4TpxKWI','fwrQE9pGizM',
            'j25j272Z9hQ','jFPz8wsQurw','7IFWkA0FM9o',
        ],
        'nako': [
            'vIcFnNdHc2w', '5YHLH9CVff0', 'o6VpbfOT9R0', 'Rry_viMzp_M',
            'rfvYiRUeK0I', 'GSVurT6v6gs', 'Lq7rgg_Rq7E', 'ucg-KHmPrXY',
            'UQD62p2TDqQ', 'PR6ZdZZiQNE', 'A-3YKK1NNJ4', 'VtxvZq6dB3Q',
            'atI1ZzBArrs', '6R5ORUUiLRQ', '-l7etfJDAso', 'MfdCxncxbQw',
            'vqHLAVx40t0', 'c-IP3n-VUm0', '-xPD5CovM70', 'DAEph5aJGlQ'
        ],
        'sakura': [
            'm2K26HTAi_E', 'eWdxzvTy88k', 'YeJ9s9Xtzug', 'qp7dHeGPi08',
            'nKcXsTOIesE', 'ywEkHQyxevQ', 'sDBPKy5jHRY', 'tnDHnbk1Pds',
            'T2Bvxr2OTUU', 'Y3RkiW0eWwQ', 'idgk0b0lioo', 'XIbrYlvCvE8',
            'DOF0M6KKw8E', 'KDfebdR8XyM', 'U_vNFe1XrlM', 'ks6fbGC2SP8',
            'Upi90X8DlbU', 'GuU_ob0diSE', '3fzXLGMFWRo', 'hdIf6j4O5TQ',
            's5oc82ZPyEs', 'nSMt0IPwAhQ', '3EkshpX5_AQ', 'f-ehRuVT19k',
            'V0WWskPWmLQ', 'W0hntlJHAXY', 'evhL6ZE4Iq0', 'tXojxAwO2R0',
            'gGpNfVCIkxU', 'zAvvJ8OxVlk', '5HjjumzgNtY', 'MXqG0e6wuY4',
            'bDAoIX1nyjY', 'xPhSvAJvbVA', 'M17XCxxAWGs', 'hcSBFdMbWVk',
            '25bEVyeTg9c', 'Hpp1oMorYNI', 'waWpOPLZPMU'
        ],
        'nayeon': [
            '6fbxCnIyS4c', 'O4XEJhLh124', 'KQiqzFmKti0', '2I8hTLs9B8c',
            'TqhQWwV9hSc', 'fhyLpq-7OL0', 'Rwyr4Q6tD4Q', 'FL6TpPBqTZk',
            'Vq2q6cLQIvc', '3iu0Y8UbRw0', 'rc35kimy7VU', 'IpvZrVPH_NE',
            'xquaIy535_c', 'ZdWfXyX-dxQ', '-RcUOYxo3tk', 'H1ky7IKp914',
            '838Bj2TTxOA'
        ]
    }

    pool = getRedisConnectionPool()
    redis = StrictRedis(connection_pool=pool)

    for key in url_ids.keys():
        ids = url_ids[key]
        print(key + ":")
        for id in ids:
            html = get_urls(url_co_prefix + id)
            soup = BeautifulSoup(html, 'html.parser')
            title = parse(soup.head.title, False)
            content = soup.find('div', {'class': 'watch-view-count'})
            viewCount = re.findall(r'\d+', parse(content, True))[0]
            delta = int(viewCount)
            if redis.exists(key, title):
                preViewCount = int(redis.hget(key, title).decode('utf-8'))
                delta = delta - preViewCount
            redis.hset(key, title, str(viewCount))
            print(delta, viewCount, title)


if __name__ == "__main__":
    main()
