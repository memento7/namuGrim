import re
import argparse
import pickle
from pathlib import Path

import pandas as pd
import orjson as json

from lib.parser import NamuParser
from lib.connection import Connection

def main(args: argparse.Namespace):
    with open(args.conf) as f:
        ctx = f.read()
    conn = Connection(**json.loads(ctx))

    if args.init:
        conn.client.indices.create(index='information')
        conn.client.indices.create(index='memento')
        return

    data_path = Path(args.data)

    if data_path.suffix == '.json':
        with data_path.open() as f:
            ctx = f.read()
        data = json.loads(ctx)
    elif data_path.suffix == '.p':
        with data_path.open('rb') as f:
            data = pickle.load(f)
    else:
        chunks = sorted(data_path.parent.glob(f'{data_path.name}*'))
        data = []
        if len(chunks) > 0:
            for chunk in chunks:
                with chunk.open('rb') as f:
                    ctx = pickle.load(f)
                data.extend(ctx)
            
    namu = NamuParser(data)

    ext_pattern = [
        "\|\|.*?본명.*?\|\|(.+?)\|\|",
        "\|\|.*?이름.*?\|\|(.+?)\|\|",
        "\|\|.*?성명.*?\|\|(.+?)\|\|",
        "\|\|.*?그룹명.*?\|\|(.+?)\|\|"
    ]

    actors = list(map(lambda x: x.split('#')[0] + '/배우', namu.get_extract('배우/한국')[3][1:]))
    singers = list(map(lambda x: x.split('#')[0] + '/가수', namu.get_extract('가수/한국')[3][1:]))
    idols = list(map(lambda x: x.split('#')[0] + '/아이돌', namu.get_extract('한국 아이돌/목록')[3][1:]))
    custom = [
        '태연(소녀시대)',
        '써니(소녀시대)',
        '티파니(소녀시대)',
        '효연(소녀시대)',
        '유리(소녀시대)',
        '수영(소녀시대)',
        '윤아(소녀시대)',
        '서현(소녀시대)',
        '제시카(가수)',
        '임나영',
        '김청하',
        '김세정',
        '정채연',
        '주결경',
        '김소혜',
        '유연정',
        '최유정',
        '강미나',
        '김도연',
        '전소미',
        '최순실',
        '박근혜',
        '문재인',
    ]
    keywords = set(actors + singers + idols + custom)

    for keyword in keywords:
        info = namu.parse_info(keyword)
        if len(info['tags']) < 30:
            print(f'{keyword} passed!')
            continue
        print(f'{keyword} inserted!')
        conn.put_data(info)
    keywords = conn.get_default_keywords()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='/backup/data/namuwiki.json')
    parser.add_argument('--conf', type=str, default='./conf/connection.json')
    parser.add_argument('--init', action='store_true', default=False)

    main(parser.parse_args())
