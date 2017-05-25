
# coding: utf-8

# # namu wiki pre-define dict

# In[1]:

import pandas as pd
import json
import re


# In[2]:

get_ipython().magic("time data = json.load(open('/backup/data/namuwiki.json'))")


# In[3]:

class NamuParser:
    def __init__(self, data):
        self.frame = pd.DataFrame(data, columns=['title', 'text'])
        self.frame.head()
        
    def get_raw(self, title):
        text = self.__get_text(title)
        return text
    
    def get_text(self, title):
        text = self.__get_text(title)
        return self.__parse_text(text)
    
    def get_extract(self, title):
        text = self.get_text(title)
        return self.__extract_text(text)
    
    def get_title(self, index):
        if index < 0 or index >= len(self): return ""
        return self.frame.loc[[index]].squeeze().title
    
    def get_id(self, title):
        loc = self.frame.loc[self.frame['title'] == title]
        if loc.empty: return -1
        return loc.index[0]
    
    def get_raw_extract(self, title, patterns):
        text = self.__get_text(title)
        return [re.findall(pattern, text) for pattern in patterns]
    
    @staticmethod
    def test(text):
        return self.__parse_text(text)
    
    @staticmethod
    def get_readable(text):
        text = text.strip()
        sub_pattern = ['\(.+\)', '\[\*.+]', '<.+?>', '--.+?--', '\{\{\{.+?\}\}\}', '~~(.+?)~~']
        rep_pattern = ['\[\[(?:.+\|)?(.+?)\]\]', "\'\'\'(.*?)\'\'\'"]
        del_pattern = ['\'', '\"']
        for pattern in sub_pattern:
            text = re.sub(pattern, '', text)
        for pattern in rep_pattern:
            text = re.sub(pattern, r'\1', text)
            
        return text.translate(str.maketrans({c:'' for c in del_pattern})).strip()
    
    def __extract_text(self, text):
        extract_label = ['링크', '취소선', '강조', 'inner링크']
        extract_pattern = ['(http.+?)[$|\]]', '~~(.+?)~~', '\'\'\'(.+?)\'\'\'', '\[\[(?:.+\|)?(.+?)\]\]']
        extracted = [ [] for _ in extract_pattern]
        
        for line in text.split('\n'):
            for i, pat in enumerate(extract_pattern):
                for match in re.findall(pat, line):
                    extracted[i].append(self.get_readable(match))
            
        return extracted
    
    def __parse_text(self, text):
        def redirect(text):
            match = re.match('^#redirect (.+)', text)
            return match and self.__get_text(match.group(1)) or text
        
        start_pattern = ['||', ' * 상위 문서 :', '== ', '=== ', '[include(틀:', '[[분류:', '[각주]', '[목차]']
        end_pattern = ['||']
        text = redirect(text)
        text = list(filter(
            lambda l: len(l.strip()) and 
                      not any(l.startswith(p) for p in start_pattern) and
                      not any(l.endswith(p) for p in end_pattern)
            , text.split('\n')
        ))
        
        return "\n".join(text)

    def __get_text(self, title):
        loc = self.frame.loc[self.frame['title'] == title]
        if loc.empty: return ""
        return loc.iloc[0].text
    
    def __getitem__(self, key):
        if isinstance(key, str):
            text = self.__get_text(key)
            return self.__parse_text(text), self.__extract_text(text)
        else:
            title, text = self.frame.iloc[key]
            return title, self.__parse_text(text), self.__extract_text(text)
    
    def __len__(self):
        h, w = self.frame.shape
        return h


# In[4]:

get_ipython().magic('time namu = NamuParser(data)')


# In[5]:

ext_pattern = [
    "\|\|.*?본명.*?\|\|(.+?)\|\|",
    "\|\|.*?이름.*?\|\|(.+?)\|\|",
    "\|\|.*?성명.*?\|\|(.+?)\|\|",
    "\|\|.*?그룹명.*?\|\|(.+?)\|\|"
]
ext_pattern2 = [
    
    "\|\|.*?멤버.*?\|\|(.+?)\|\|",
]


# In[6]:

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
keywords = set(actors[400:600] + singers[100:300] + idols + custom)


# In[7]:

ext_pattern = [
    "\|\|.*?본명.*?\|\|(.+?)\|\|",
    "\|\|.*?이름.*?\|\|(.+?)\|\|",
    "\|\|.*?성명.*?\|\|(.+?)\|\|",
    "\|\|.*?그룹명.*?\|\|(.+?)\|\|"
]


# In[8]:

from konlpy.tag import Twitter; tagger = Twitter()
from collections import Counter
from functools import reduce
from itertools import chain
from KINCluster import stopwords


# In[9]:

def parse_info(keyword):
    print (keyword)
    if '/' not in keyword:
        key = keyword
        origin_sub = ''
    else:
        key, origin_sub, *_ = keyword.split('/')
    
    def _parse_name(q):
        return map(lambda x: list(filter(len, map(namu.get_readable, x))), 
                        namu.get_raw_extract(q, ext_pattern))
    
    def _count_noun(text):
        return Counter(tagger.nouns(text))
    
    def _count_least(counter, least=1):
        return filter(lambda x: x[1]>least, counter)
    
    def _parse_text(q):
        return namu.get_readable(namu.get_text(q))
    
    tags = Counter()
    ext_link, ext_strike, ext_accent, ext_inlink = [],[],[],[]
    for sub in ['', origin_sub, '배우', '연예인', '가수']:
        q = key + (sub and '({})'.format(sub))
        real, name, stat, group = _parse_name(q)
        if real or name or stat:
            break

    if not real and not name and not stat:
        q = key
        
    ext_link, ext_strike, ext_accent, ext_inlink = namu.get_extract(q)
    tags = reduce(lambda x, y: x + y, [
        Counter({k:v*50 for k, v in _count_least(_count_noun(_parse_text(q)).items())}),
        Counter({k:v*150 for k, v in _count_noun(" ".join(ext_accent)).items()})
    ] + list(map(lambda x: Counter({k:v for k, v in _count_least(_count_noun(_parse_text(x)).most_common()[:25], 10)}), ext_inlink)))
    tags = list(map(lambda x: {
                'tag': x[0],
                'value': x[1]
            }, Counter({k:v for k, v in tags.items() if k not in stopwords}).most_common()))
    
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


# In[10]:

from elasticsearch import Elasticsearch
es = Elasticsearch(host='server2.memento.live')


# In[61]:

keywords = es.search(index='information', doc_type='namugrim', size=1000)


# In[62]:

len(keywords['hits']['hits'])


# In[72]:

def get_keywords():
    def _get_scroll_(scroll):
        scroll_doc = scroll['hits']['hits']
        return len(scroll_doc), scroll_doc
    keywords = []
    scroll = es.search(index='information', doc_type='namugrim', scroll='1m', size=1000)
    scroll_id = scroll['_scroll_id']
    scrolled, scroll_doc = _get_scroll_(scroll)
    keywords.extend(scroll_doc)
    while scrolled:
        scroll = es.scroll(scroll_id=scroll_id, scroll='1m')
        scrolled, scroll_doc = _get_scroll_(scroll)
        keywords.extend(scroll_doc)
    return keywords


# In[88]:

def make_clear(results, key_lambda = lambda x: x['_id'], value_lambda = lambda x: x, filter_lambda = lambda x: x):
    def clear(result):
        result['_source']['_id'] = result['_id']
        return result['_source']
    iterable = filter(filter_lambda, map(clear, results))
    return {key_lambda(source): value_lambda(source) for source in iterable}


# In[ ]:

def put_data(info: dict):
    def exist(keyword):
        return es.search(index='information', doc_type='namugrim', body={
            'query': {
                'match': {
                    'keyword': keyword,
                }
            }    
        })['hits']['total'] != 0
    if exist(info['keyword']):
        # TODO: update
        return
    es.index(index='information', doc_type='namugrim', id=info['keyword'], body=info)


# In[ ]:

for keyword in keywords:
#for keyword in ['김태희', '비', '공유', '수지']:
    info = parse_info(keyword)
    if len(info['tags']) < 30:
        print ('passed!')
        continue
    put_data(info)


# In[ ]:

print('done')


# In[101]:

es.search(index='information', doc_type='News_Naver')


# In[100]:

es.search(index='information', doc_type='namugrim', body={
    'query': {
        'match': {
            'keyword': '수지'
        }
    }
})['hits']['hits'][0]['_source']['subkey']


# In[ ]:



