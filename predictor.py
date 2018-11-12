#!/usr/bin/python
# -*- coding: utf-8 -*-
import keras
import numpy as np
import json
import pymorphy2 as py
morph = py.MorphAnalyzer()
stress_char = "ре́с"[2]

MAX_LENGTH = 26
feat = ['aspect', 'case', 'POS', 'mood', 'gender', 'number', 'person', 'tense', 'voice', 'transitivity']

def prepare_data(key):
    key = key.replace('ѝ', 'й')[::-1]
    word = morph.parse(key)[0]
    row = [0] * (MAX_LENGTH + len(feat))
    for i in range(len(feat)):
        try:
            row[i] = cnt[i][eval('word.tag.' + feat[i])] / len(cnt[i])
        except:
            pass
    for i in range(len(key)):
        row[len(feat) + i] = c2id[key[i]] / len(c2id)
    return np.array(row)

model = keras.models.load_model('model.h5')
c2id = json.loads(open('c2id.json', encoding='utf-8').read())
cnt = json.loads(open('back.json').read())
vow = 'уеыаоэяиюё'

def predict_stress(data):
	"""
	A function to predict stress in words.
	:param data - iterable object of words
	:return - list of stress positions in these words.
	"""
	to_pred = np.array([prepare_data(key) for key in data])
	one_hot = model.predict(to_pred)
	res = []
	ind = 0
	for el in one_hot:
		cnt = 0
		pos = 0
		ok = False
		for c in data[ind]:
			if c in vow:
				cnt += 1
				if c == 'ё':
					pos = cnt - 1
					ok = True
					break
		if ok:
			res.append(pos)
			continue
		print(el)
		for i in range(cnt):
			if el[i] > el[pos]:
				pos = i
		res.append(cnt - pos - 1)
		ind += 1
	return res

if __name__ == "__main__":
	while True:
		word = input()
		print(predict_stress([word]))
		pass