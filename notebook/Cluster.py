
# coding: utf-8

# In[1]:

import pandas as pd
from konlpy.tag import Twitter

# In[4]:

def getContents(actor):
    return contents.loc[contents['actor'] == actor]

# In[5]:

tagger = Twitter()

def getTokens(content):
    if content != content: return ''
    return ["{}/{}".format(word, tag) for word, tag in tagger.pos(content) if tag == 'Noun']

def extract(tokens, n=15):
    token_dic = {}
    for token in tokens:
        if not token in token_dic: token_dic[token] = 0
        token_dic[token] += 1
    tokens = sorted(list(token_dic.items()), key = lambda x: -x[1])
    return tokens[:n]

def tokenize(content):
    return extract(getTokens(content), 25)


# In[ ]:

fileName = 'check.json'
import json
loaded = False
from os.path import isfile
contents = []
def load():
    global loaded
    global contents
    print ('load')
    loaded = True
    if isfile(fileName): 
        with open(fileName, 'r') as chk:
            ret = json.load(chk)
        contents = pd.read_csv(open('../../newsCraw/data/newsTag-' + ret['idx'] + '.csv', 'rU'), encoding='utf-8', engine='c')
        print(contents.shape)
        return int(ret['idx'])
    contents = pd.read_csv('../../newsCraw/data/newsContents.csv')
    print (contents.shape)
    return 0

def save(idx):
    print ('save: ' + str(idx))
    ret = {}
    ret['idx'] = str(idx)
    with open(fileName, 'w') as chk:
        json.dump(ret, chk) 


# In[ ]:

ldx = load()
for idx, content in contents.iterrows():
    if idx < ldx: continue 
    if not idx % 10000:
        print('start saving')
        contents.to_csv('../../newsCraw/data/newsTag-' + str(idx) + '.csv')
        save(idx)
    contents.set_value(idx, 'tokens', tokenize(content.content))


# In[ ]:

contents.to_csv('../../newsCraw/data/newsTag.csv')


# In[ ]:

print ('done')

