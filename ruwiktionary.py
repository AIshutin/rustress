#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
рассветать
COMP
женись
"""

import requests as rq
import bs4
import json
import random as rd
import os
from copy import deepcopy

from time import sleep
import pprint
import pymorphy2 as py

stress_char = "ре́с"[2]
not_found = "@"
morph = py.MorphAnalyzer()

def normal_form(stressed):
	return stressed.replace(stress_char, '')

def is_stressed(form):
	return form.find(stress_char) != -1

def make_stressed(word):
    """
    A function that marks first vowel as stressed
    :param word
    :return stressed word
    """
    ans = ""
    was = False
    for el in word:
        ans += el
        if el in vowels and not was:
            ans += stress_char
            was = True
    return ans

def get_text(bs):
	text = []
	state = 0
	'''
	0 1 1 0
	ab<cd >
	'''
	curr = str(bs).replace('<br/>', ' ')
	for el in curr:
		if state == 0:
			if el == '<':
				state = 1
			else:
				text.append(el)
		elif state == 1:
			if el == '>':
				state = 0
	return "".join(text)

def clean_word(stressed):
	res = []
	for el in stressed:
		if el.isalpha() or el == stress_char:
			res.append(el)
	return ''.join(res)

def find_formstress(table):
    """
    A function to find the stress of the some word form.
    :param word - Parse object
    :param table - parsed html tables array with stress information
    :return - word with stress
    """
    if table is None:
        return dict()

    final = set()

    for POS in {'NOUN', 'ADJF', 'ADJS', 'PRTF', 'PRTS', 'VERB', 'GRND', 'ADVB'}:
	    if POS == 'NOUN':
	        need = table[POS]
	        whois = 'N'
	    elif POS in {'ADJF', 'ADJS', 'PRTF', 'PRTS'}:
	        need = table['ADJ']
	        whois = 'A'
	    elif POS in {'VERB', 'GRND'}:
	        need = table['VERB']
	        whois = 'V'
	    else:
	        need = table['ADVB']
	        whois = 'O' #others
	    if len(need) > 1:
	        need = need[:1]
	    if len(need) == 0:
	    	continue

	    need = need[0]

	    eng2rus = {'nomn': 'именительный', 'gent': 'родительный', 
	               "datv": "дательный", "accs": "винительный",
	               "ablt": "творительный", "loct": "предложный",
	               "gen2": "родительный", "loc2": "предложный",
	               "voct": "звательный падеж", None: "краткая форма"}
	    genders = {'masc': 0, 'femn': 2, 'neut': 1, None: 3}

	    if whois == 'N':
	        dictlike = dict()
	        for tr in need.find_all('tr'):
	            td = tr.find_all('td')
	            if len(td) == 0:
	                continue
	            formes = [get_text(el).rstrip() for el in td[1:3]]
	            for form in formes:
	                final.update(form.split())
	    elif whois == 'A':
	        for tr in need.find_all('tr'):
	            td = tr.find_all('td')
	            if len(td) == 0:
	                continue
	            formes = [get_text(el).rstrip() for el in td[1:5]]
	            for form in formes:
	            	final.update(form.split())
	    elif whois == 'V':
	        present = {('2per', 'sing'): "ты", ('1per', 'sing'): "я", 
	                        ('3per', 'sing'): "он", ('1per', 'plur'): "мы", 
	                        ('2per', 'plur'): "вы", ('3per', 'plur'): "они"}
	        for tr in need.find_all('tr'):
	            td = tr.find_all('td')
	            if len(td) == 0:
	                continue
	            title = (td[0].find('a')).attrs['title']
	            formes = [get_text(el).rstrip() for el in td[1:4]]
	            for form in formes:
	            	final.update(form.split())
	    else:
	        final.add(need)
    clear = dict()
    for el in final:
    	if is_stressed(el):
    		el = clean_word(el)
    		clear[normal_form(el)] = el
    return clear

class StressDB:
    articles = dict()

    def load(self, filename):
        with open(filename, encoding='utf-8') as file:
            self.articles = json.loads(file.read())

    def __init__(self, source=None):
        self.articles = dict()
        if source is not None:
            self.load(source)

    def save(self, filename):
        with open(filename, 'w') as file:
            print(json.dumps(self.articles), file=file)

    def get_stress(self, parse):
	    objhash = parse.normal_form
	    if objhash not in self.articles:
	       	try:
	       		res = find_formstress(get_stress(parse))
	       	except Exception as exp:
	       		if exp.args[0] != 'Page not found':
	       			raise
	       		print(exp)
	       		return not_found
	        for form in res:
	        	self.articles[form] = res[form]
	    if parse.word in self.articles:
	    	return self.articles[parse.word]
	    else:
	   		return not_found

    def __len__(self):
        return len(self.articles)

def get_stress(word):
    """
    Function to get stress.
    :param word: Parse object from pymorphy2
    :return: index of stressed letter
    """

    if "LATN" in word.tag:
        raise Exception("Page not found")

    url = "https://ru.wiktionary.org/wiki/"
    normal = word.normal_form

    endings = {'а', 'ы', "о"}

    if word.tag.POS == 'PRTF':
        normal = word.word[:-2] + 'ый'
    elif word.tag.POS == 'PRTS':
        normal = word.word
        if normal[-1] in endings:
            normal = normal[:-1]
        normal += 'ный'
    print(normal, word.tag, flush=True)
    #try:
    print("SENT", flush=True)
    resp = rq.get(url + normal)
    print("GOT", flush=True)
    print(resp.status_code, flush=True)
    #except:
    #    raise Exception("Timeout")
    if (resp.status_code != 200):
        raise Exception("Page not found")
    bs = bs4.BeautifulSoup(resp.text, 'html.parser')
    return get_essences(bs, normal)

def get_essences(article, word):
    """
    Extracts all descriptions from the wiktionary article.
    :param article: Beatiful soup with article
    :param word: normal formal of word we are searching stress of.
    :return: list of Beatiful soups
    """
    interesting = dict()
    interesting['NOUN'] = article.find_all("table",
                     attrs={"style": "float:right; clear:right; margin-left:0.5em; margin-bottom:0.5em; border: 1px solid #6699CC; border-collapse:collapse;",
                            "cellpadding": "2", "rules": "all", "width": "250"}) #noun
    #                        "style": "float:right; clear:right; margin-left:0.5em; margin-bottom:0.5em; border: 1px solid #6699CC; border-collapse:collapse;"
    interesting['VERB'] = article.find_all("table",
                     attrs={"style": "float:right; clear:right; padding:3; margin-left:0.5em; margin-bottom:0.5em; border: 1px solid #6699CC; border-collapse:collapse;",
                            "cellpadding": "2", "rules": "all"}) #verb
    interesting['ADJ'] = article.find_all("table", 
                     attrs={"style": "float:right; clear:right; margin-left:0.5em; margin-bottom:0.5em; border: 1px solid #6699CC; border-collapse:collapse;", 
                            "cellpadding": "2", "rules":"all"}) #adjective
    
    b = article.find_all('b')
    poss = []
    for el in b:
        ok = True
        has_stress = False
        cnt = dict()
        for c in word:
            if c not in cnt:
                cnt[c] = 1
            else:
                cnt[c] += 1
        for c in el.text:
            if c == stress_char:
                has_stress = True
                continue
            if c.isalpha():
                if c not in cnt:
                    ok = False
                else:
                    cnt[c] -= 1
                continue
            if c == '-':
                continue
            ok = False
        if ok and has_stress:
            poss.append(el.text.replace('-', ''))
    poss = list(set(poss))
    interesting['ADVB'] = poss
    return interesting

if __name__ == "__main__":
    if "stressdb.json" in os.listdir("."):
        db = StressDB("stressdb.json")
        assert(len(db) >= 7)
    else:
        db = StressDB()
    print(len(db))
    print("LENGTH")
    morph = py.MorphAnalyzer()

    with open("out.txt", encoding="utf-8") as file:
        words = set()
        word = ""
        for el in file.read() + "#":
            if el.isalpha():
                word += el
            else:
                if len(word) != 0:
                    words.add(word.lower())
                    word = ""
        last = len(db)
        for word in words:
            try:
                print("word:", word, flush=True)
                print(word, db.get_stress(morph.parse(word)[0]))
                if (len(db) - last) % 400 == 0 and len(db) != last:
                    print("SAVED", len(db))
                    db.save("db-stress-" + str(len(db)) + ".txt")
                    db.save("stressdb.json")
                    db = StressDB('stressdb.json')
                    last = len(db)
                    sleep(60)
                    print("COMPLEATED")
                    #break
            except Exception as exp:
                print("!!!!!!!!!!!!!!!!!!!!!!")
                print(exp)
                print()
                print()
                db = StressDB('stressdb.json')
                last = len(db)
                sleep(180)
                print("continued")
