
# coding: utf-8

# # namu wiki pre-define dict

# In[1]:

import pandas as pd
import json
import re


# In[2]:

get_ipython().magic("time data = json.load(open('/backup/data/namuwiki.json'))")


# In[102]:

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


# In[103]:

get_ipython().magic('time namu = NamuParser(data)')


# In[52]:

actors = list(map(lambda x: x.split('#')[0] + '/배우', namu.get_extract('배우/한국')[3][1:]))
singers = list(map(lambda x: x.split('#')[0] + '/가수', namu.get_extract('가수/한국')[3][1:]))
keywords = set(actors + singers)


# In[53]:

ext_pattern = [
    "\|\|.*?본명.*?\|\|(.+?)\|\|",
    "\|\|.*?이름.*?\|\|(.+?)\|\|",
    "\|\|.*?성명.*?\|\|(.+?)\|\|",
    "\|\|.*?그룹명.*?\|\|(.+?)\|\|"
]


# In[54]:

from konlpy.tag import Twitter; tagger = Twitter()
from collections import Counter
from functools import reduce
from itertools import chain
from KINCluster import stopwords


# In[55]:

def parse_info(keyword):
    key, origin_sub = keyword.split('/')
    
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
        q = key + sub or '({})'.format(sub)
        real, name, stat, group = _parse_name(q)
        if real or name or stat:
            ext_link, ext_strike, ext_accent, ext_inlink = namu.get_extract(q)
            tags = reduce(lambda x, y: x + y, [
                Counter({k:v*50 for k, v in _count_least(_count_noun(_parse_text(q)).items())}),
                Counter({k:v*150 for k, v in _count_noun(" ".join(ext_accent)).items()})
            ] + list(map(lambda x: Counter({k:v for k, v in _count_least(_count_noun(_parse_text(x)).most_common()[:25], 10)}), ext_inlink)))
            tags = Counter({k:v for k, v in tags.items() if k not in stopwords}).most_common()
            break

    if stat and not name: name = stat[0]
    
    group = group and group[0] or ""
    name = name and name[0] or key
    real = real and real[0] or name
    
    return {
        'group': group,
        'keyword': key,
        'realname': real,
        'nickname': name,
        'subkey': sub,
        'tags': tags,
        'outlinks': ext_link,
        'inlinks': ext_inlink,
        'strikes': ext_strike,
        'accents': ext_accent
    }


# In[56]:

import pymysql
from os import environ
SERVER_RDB = 'server2.memento.live'


# In[72]:

conn = pymysql.connect(host=SERVER_RDB,
                       user='memento', 
                       passwd=environ['MEMENTO_PASS'], 
                       db='memento',
                       charset='utf8')
cur = conn.cursor()


# In[58]:

def get_last_id():
    q = "SELECT LAST_INSERT_ID()"
    r = cur.execute(q)
    return cur.fetchone()[0]


# In[59]:

entity_column = {
    'entity': ['keyword', 'subkey', 'realname', 'nickname'],
    'entity_accent': ['target', 'accent'],
    'entity_strike': ['target', 'strike'],
    'entity_link': ['target', 'link', 'flag'],
    'entity_tag': ['target', 'tag', 'count']
}


# In[60]:

def insert_query(table, info):
    q = "INSERT INTO {} ({}) VALUES ({})".format(
        table,
        ",".join(entity_column[table]),
        ",".join("\'{}\'".format(info[c]) for c in entity_column[table])
    )
    cur.execute(q)
    conn.commit()


# In[61]:

def push_db(info: dict):
    insert_query('entity', info)
    target = get_last_id()
    
    info['target'] = target
    
    for accent in info['accents']:
        info['accent'] = accent
        insert_query('entity_accent', info)
    
    for strike in info['strikes']:
        info['strike'] = strike
        insert_query('entity_strike', info)
    
    for link in info['inlinks']:
        info['link'] = link
        info['flag'] = 0
        insert_query('entity_link', info)
        
    for link in info['outlinks']:
        info['link'] = link
        info['flag'] = 1
        insert_query('entity_link', info)
        
    for tag, count in info['tags']:
        info['tag'] = tag
        info['count'] = count
        insert_query('entity_tag', info)


# In[104]:

flag = False
for keyword in keywords:
    if keyword.startswith('강수지'): flag = True
    if not flag: continue
    info = parse_info(keyword)
    push_db(info)


# In[105]:

cur.close()
conn.close()


# In[ ]:



