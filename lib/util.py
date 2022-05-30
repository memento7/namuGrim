import typing
from collections import Counter
from functools import reduce

from konlpy.tag import Twitter; tagger = Twitter()
from KINCluster import stopwords


def parse_info(keyword, ext_pattern: typing.List[str]) -> typing.Dict[str, typing.Any]:
    if '/' not in keyword:
        key = keyword
        origin_sub = ''
    else:
        key, origin_sub, *_ = keyword.split('/')
    
    def _parse_name(q):
        return map(
            lambda x: list(filter(len, map(namu.get_readable, x))), 
            namu.get_raw_extract(q, ext_pattern)
        )
    
    def _count_noun(text):
        return Counter(tagger.nouns(text))
    
    def _count_least(counter, least=1):
        return filter(lambda x: x[1] > least, counter)
    
    def _parse_text(q):
        return namu.get_readable(namu.get_text(q))
    
    tags = Counter()
    ext_link, ext_strike, ext_accent, ext_inlink = [],[],[],[]
    for sub in ['', origin_sub, '배우', '연예인', '가수']:
        q = key + (sub and f'({sub})')
        real, name, stat, group = _parse_name(q)
        if real or name or stat:
            break

    if not real and not name and not stat:
        q = key
        
    ext_link, ext_strike, ext_accent, ext_inlink = namu.get_extract(q)
    tags = reduce(lambda x, y: x + y, [
        Counter({k: v * 50 for k, v in _count_least(_count_noun(_parse_text(q)).items())}),
        Counter({k: v * 150 for k, v in _count_noun(" ".join(ext_accent)).items()})
    ] + list(map(lambda x: Counter({k:v for k, v in _count_least(_count_noun(_parse_text(x)).most_common()[:25], 10)}), ext_inlink)))

    tags = [
        {
            'tag': tag,
            'value': value,
        } for tag, value in Counter({k:v for k, v in tags.items() if k not in stopwords}).most_common())
    ]

    if stat and not name: name = stat[0]
    
    group = group and group[0] or ""
    name = name and name[0] or key
    if len(name) > 32: name = name[:3]
    real = real and real[0] or name
    
    return {
        'group': group,
        'keyword': key,
        'realname': real,
        'nickname': name,
        'subkey': sub,
        'tags': tags,
        'outlinks': list(set(ext_link)),
        'inlinks': list(set(ext_inlink)),
        'strikes': ext_strike,
        'accents': ext_accent
    }


def make_clear(
    results,
    key_lambda = lambda x: x['_id'],
    value_lambda = lambda x: x,
    filter_lambda = lambda x: x
):
    def clear(result):
        result['_source']['_id'] = result['_id']
        return result['_source']

    return {
        key_lambda(source): value_lambda(source)
        for source in filter(filter_lambda, map(clear, results))
    }
