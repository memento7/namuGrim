
# coding: utf-8

# In[1]:

from konlpy.tag import Twitter
import pandas as pd
import pickle
import re


# In[2]:

tagger = Twitter()


# ## load pickle

# In[8]:

with open('/backup/namuGrim/data/namuwiki.p', 'rb') as f:
    frame = pickle.load(f)


# In[9]:

print (frame.shape)
frame.head(3)


# In[10]:

def get_article(title):
    p = frame.loc[frame['title'] == title]
    if p.empty:
        return ""
    return p.text.values[0]


# In[11]:

pat_redirect = re.compile('^#redirect (.+)')
pat_index = re.compile('(.+?)\#(.+)')
def redirect_filter(text):
    match = pat_index.match(text)
    if match:
        return match.group(1)
    return text

def check_redirect(text):
    match = pat_redirect.match(text)
    if match:
        return redirect_filter(match.group(1).strip())
    else:
        return False


# In[12]:

pat_bracket = re.compile(r'\[\[(.+?)\]\]')
pat_file = re.compile(r'\[\[파일:(.+)\]\]')
pat_link = re.compile(r'\[\[(.+?)\|(.+?)\]\]')
pat_comment = re.compile(r'\[\*(.+?)\]')
pat_high = re.compile(r'\{\{\{(.+?)\}\}\}')
pat_frame = re.compile(r'\[include\(틀:(.+?)\)\]')

def article_filter(text):
    chk = check_redirect(text)
    if chk:
        text = get_article(chk)
    return text

def bracket_filter(text):
    ret = ""
    match = pat_file.match(text)
    if match: 
        ret = ""
    else:
        match = pat_link.match(text)
        if match: 
            ret = match.group(2)
        else:
            ret = text[2:-2]
    return ret

def context_filter(text):
    # find frame
    delc = 0
    matches = pat_frame.finditer(text)
    for match in matches:
        conv = match.group(1)
        text = text[:match.start() - delc] + conv + text[match.end() - delc:]
        delc += len(match.group(0)) - len(conv)
    
    # find bracket
    delc = 0
    matches = pat_bracket.finditer(text)
    for match in matches:
        conv = bracket_filter(match.group(0))
        text = text[:match.start() - delc] + conv +  text[match.end() - delc:]
        delc += len(match.group(0)) - len(conv)
        
    # comments
    delc = 0
    matches = pat_comment.finditer(text)
    for match in matches:
        text = text[:match.start() - delc] + match.group(0) +  text[match.end() - delc:]
        delc += 3
        
    # find highlight
    delc = 0
    matches = pat_high.finditer(text)
    for match in matches:
        text = text[:match.start() - delc] + match.group(1) +  text[match.end() - delc:]
        delc += 6
    
    return text


# In[13]:

def tokenize(content): 
    if len(content) > 8192:
        return tokenize(content[:8192]) + tokenize(content[8192:])
    else:
        return ["{}/{}".format(word, tag) for word, tag in tagger.pos(content) if tag == 'Noun']


# In[14]:

class Words:
    def __init__(self, frame, filt = lambda x: x):
        self.frame = frame
        self.filt = filt
    
    def __iter__(self):
        for _, article in self.frame.iterrows():
            yield self.filt(article)


# # word2vec

# In[16]:

import gensim


# In[17]:

namuWords = Words(frame, filt=lambda x : tokenize(context_filter(article_filter(x.text))))


# In[18]:

namuTrains = Words(frame, filt=lambda x : tokenize(context_filter(article_filter(x.text))))


# In[21]:

model = gensim.models.Word2Vec(window=5000)


# In[ ]:

model.build_vocab(namuWords)


# In[ ]:

model.train(namuTrains)


# In[ ]:

model.save('../data/model')


# In[ ]:

model.most_similar('아이유/Noun')

