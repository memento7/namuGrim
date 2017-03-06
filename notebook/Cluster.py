
# coding: utf-8

# In[1]:

import pandas as pd
from konlpy.tag import Twitter

# In[13]:

contents = pd.read_csv('../../newsCraw/data/newsContents.csv')
print (contents.shape)

# In[8]:

def getContents(actor):
    return contents.loc[contents['actor'] == actor]

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

fileName = 'check.json'
import json
loaded = False
from os.path import isfile
def load():
    global loaded
    print ('load')
    loaded = True
    if isfile(fileName): 
        with open(fileName, 'r') as chk:
            ret = json.load(chk)
        return int(ret['idx'])
    return 0

def save(idx):
    print ('save: ' + str(idx))
    ret = {}
    ret['idx'] = str(idx)
    with open(fileName, 'w') as chk:
        json.dump(ret, chk) 

print ('start')
for idx, content in contents.iterrows():
    if not loaded: ldx = load()
    if idx < ldx: continue 
    if not idx % 10000:
        print('start saving')
        contents.to_csv('../../newsCraw/data/newsTag-' + str(idx) + '.csv')
        save(idx)
    content.tokens = tokenize(content.content)

print('done.')
# In[ ]:


