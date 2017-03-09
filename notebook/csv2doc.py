
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


# # ko-Wikipedia

# In[4]:

kowiki = pickle.load(open('../data/kowiki.p','rb'))


# In[5]:

print (kowiki.shape)
kowiki.head(3)


# # Namu Wiki

# In[6]:

namuwiki = pickle.load(open('../data/namuwiki.p', 'rb'))


# In[7]:

print (namuwiki.shape)
namuwiki.head(3)


# # Tokenize

# In[8]:

from konlpy.tag import Twitter
tagger = Twitter()
def tokenize(content):
    if content != content: return ''
    return [ word for word, tag in tagger.pos(content) if tag == 'Noun']


# In[ ]:

with open('../data/kowiki.txt', 'w') as f:
    for idx, content in kowiki.iterrows():
        f.write(" ".join(tokenize(content.text)) + "\n")


# In[ ]:

with open('../data/namuwiki.txt', 'w') as f:
    for idx, content in namuwiki.iterrows():
        f.write(" ".join(tokenize(content.text)) + "\n")


# ## check point
