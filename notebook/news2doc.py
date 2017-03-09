
# coding: utf-8

# In[1]:

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division


# In[2]:

import numpy as np
import pandas as pd
#import tensorflow as tf
import matplotlib.pyplot as plt
import json
import re
import pickle


# In[3]:

import collections
import math
import os
import random
import zipfile


# # naver News Content

# In[4]:

contents = pd.read_csv('../../newsCraw/data/newsContents.csv')


# In[5]:

print (contents.shape)
contents.head(3)


# # Tokenize

# In[6]:

from konlpy.tag import Twitter
tagger = Twitter()
def tokenize(content):
    if content != content: return ''
    return [ word for word, tag in tagger.pos(content) if tag == 'Noun']


# In[7]:

filename = 'check.json'
from os.path import isfile
def load():
    idx = 0
    if isfile(filename):
        with open(filename, 'r') as f:
            ldx = json.load(f)
        idx = int(ldx['idx'])
    return idx

def save(idx):
    print('save ' + str(idx))
    ldx = {}
    ldx['idx'] = str(idx)
    with open(filename, 'w') as f:
        json.dump(ldx, f)


# In[13]:

step = 50000
l, _ = contents.shape
idx = load()


# In[ ]:

for i in range(idx, l, step):
    print (i,step)
    frame = contents.iloc[i:i+step]
    print (frame.shape)
    with open('../../newsCraw/data/newsContents.txt', 'a') as f:
        for idx, content in frame.iterrows():
            f.write(" ".join(tokenize(content.content)))
    save (i)


# In[ ]:



