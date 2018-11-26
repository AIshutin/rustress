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
chars_ln = 57

def prepare_data(key):
    key = key.replace('ѝ', 'й')[::-1]
    word = morph.parse(key)[0]
    row = np.zeros(MAX_LENGTH * chars_ln + sum(cnts), dtype=np.bool)
    curr = 0
    for i in range(len(feat)):
        try:
            row[curr + feat2id[eval('word.tag.' + feat[i])]] = 1
        except:
            pass
        curr += cnts[i]
    for i in range(len(key)):
        row[curr + c2id[key[i]] - 1] = 1
        curr += chars_ln
    return row

model = keras.models.load_model('model.h5')
c2id = json.loads(open('c2id.json', encoding='utf-8').read())
feat2id = json.loads(open('back.json').read())
cnts = [len(feat2id[i]) for i in range(len(feat))]


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
			cnt += 1
			if c == 'ё':
				pos = cnt - 1 
				ok = True
				break
		if ok:
			res.append(pos)
			continue
		vow_pos = 0
		for i in range(cnt):
			if data[ind][-i - 1] in vow:
				vow_pos = cnt - i - 1
			if el[i] > el[pos]:
				pos = i
		if data[ind][cnt - pos - 1] not in vow:
			res.append(vow_pos)
			continue
		res.append(cnt - pos - 1)
		ind += 1
	return res

if __name__ == "__main__":
	while True:
		word = input()
		print(predict_stress([word]))
		pass