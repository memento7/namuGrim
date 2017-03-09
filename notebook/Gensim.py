# coding: utf-8

import numpy as np
import pandas as pd

import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

config = {
    'min_count': 5,  # 등장 횟수가 5 이하인 단어는 무시
    'sg': 1,  # 0이면 CBOW, 1이면 skip-gram을 사용한다
    'iter': 100,  # 보통 딥러닝에서 말하는 epoch과 비슷한, 반복 횟수
    'workers': multiprocessing.cpu_count(),
}
model = Word2Vec()

model.build_vocab(LineSentence('../data/vocab.txt'))
model.train(LineSentence('../data/vocab.txt'))

model.save('../data/model')
