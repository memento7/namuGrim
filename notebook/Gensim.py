
# coding: utf-8

# In[ ]:

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division


# In[ ]:

import numpy as np
import pandas as pd
#import tensorflow as tf
import matplotlib.pyplot as plt
import json
import re
import pickle


# In[ ]:

import collections
import math
import os
import random
import zipfile


# # ko-Wikipedia

# In[ ]:

kowiki = pickle.load(open('../data/kowiki.p','rb'))


# In[ ]:

print (kowiki.shape)
kowiki.head(3)


# # Namu Wiki

# In[ ]:

namuwiki = pickle.load(open('../data/namuwiki.p', 'rb'))


# In[ ]:

print (namuwiki.shape)
namuwiki.head(3)


# In[ ]:

def tokenize(content):
    if content != content: return ''
    return ["{}/{}".format(word, tag) for word, tag in tagger.pos(content) if tag == 'Noun']


# In[ ]:

class SentenceReader:
    def __init__ (self, frame, filt=lambda x: tokenize(x.text)):
        self.frame = frame
        self.filt = filt
    
    def __iter__ (self):
        for idx, content in self.frame.iterrows():
            yield self.filt(content)        


# In[ ]:

from konlpy.tag import Twitter
tagger = Twitter()


# In[ ]:

import gensim


# In[ ]:

filename = 'gensim.json'


# In[ ]:

from os.path import isfile
def load():
    idx = 0
    if isfile(filename):
        with open(filename, 'r') as f:
            ldx = json.load(f)
            idx = int(ldx['idx'])
    return idx


# In[ ]:

def save(idx):
    ldx = {}
    ldx['idx'] = str(idx)
    with open(filename, 'w') as f:
        json.dump(ldx, f)


# In[ ]:

l, _ = kowiki.shape
step = 1000
ldx = load()
model = ldx and gensim.models.Word2Vec.load('../data/model') or gensim.models.Word2Vec()


# In[ ]:

if not ldx:
    print ('start build vocab kowiki')
    model.build_vocab(SentenceReader(kowiki))
    model.save('../data/model')
    print ('done build vocab')


# In[ ]:

print ('start train vocab kowiki')
for idx in range(ldx, l, step):
    print (idx)
    model.train(SentenceReader(kowiki[idx:step]))
    model.save('../data/model')


# In[ ]:

print ('done')


# In[ ]:

#sentence_vocab = SentenceReader(namuwiki)
#sentence_train = SentenceReader(namuwiki)


# In[ ]:

#print ('namuwiki- build vocab')
#model.build_vocab(sentence_vocab)


# In[ ]:

#print ('namuwiki- train')
#model.train(sentence_train)


# In[ ]:

#model.save('../data/model')

