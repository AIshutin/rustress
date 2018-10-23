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
from time import sleep
from fake_useragent import UserAgent
import os


stress_char = "ре́с"[2]
not_found = "@"
vowels = "уяаюыеи"

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

def check(word, stressed):
    """
    Checks if stressed form is related to word.
    :param word - a word without stress
    :param stressed - stressed form of a word
    :return bool
    """
    d = dict()
    for el in word:
        if el not in d:
            d[el] = 0
        d[el] += 1
    for el in stressed:
        if stress_char == el:
            continue
        if el not in d:
            return False
        d[el] -= 1
    for el in d:
        if d[el] != 0:
            return False
    return True


def find_formstress(word, table):
    """
    A function to find the stress of the some word form.
    :param word - Parse object
    :param table - parsed html tables array with stress information
    :return - word with stress
    """
    if table is None:
        return not_found
    if sum(word.word.count(vow) for vow in vowels) <= 1:
        return make_stressed(word.word)

    POS = word.tag.POS 
    need = whois = None

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

    #print(need)
    if len(need) > 1:
        need = need[:1]
        #raise Exception("Too many variants", need)
    if len(need) == 0:
        return not_found
        raise Exception('No variants')

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
            formes = [el.text.rstrip() for el in td[1:3]]
            title = (td[0].find('a')).attrs['title']
            dictlike[title] = formes
        res = dictlike[eng2rus[word.tag.case]][0 if word.tag.number != 'plur' else 1]
        if check(word.word, res):
            return res
        else:
            return not_found
    elif whois == 'A':
        dictlike = dict()
        for tr in need.find_all('tr'):
            td = tr.find_all('td')
            if len(td) == 0:
                continue
            formes = [el.text.rstrip() for el in td[1:5]]
            title = (td[0].find('a')).attrs['title']
            dictlike[title] = formes
        try:
            res = dictlike[eng2rus[word.tag.case]][genders[word.tag.gender]]
        except:
            return not_found
        if not check(word.word, res):
            return not_found
        return res
    elif whois == 'V':
        dictlike = dict()
        present = {('2per', 'sing'): "ты", ('1per', 'sing'): "я", 
                        ('3per', 'sing'): "он", ('1per', 'plur'): "мы", 
                        ('2per', 'plur'): "вы", ('3per', 'plur'): "они"}
        past_gend = [None] * 3
        for tr in need.find_all('tr'):
            td = tr.find_all('td')
            if len(td) == 0:
                continue
            title = (td[0].find('a')).attrs['title']
            if title == 'он':
                s = str(td[2])
                s = s[s.find('>') + 1:s.rfind('<')]

                past_gend = [el.rstrip() for el in list(s.split('<br/>'))]
                    
            formes = [el.text.rstrip() for el in td[1:4]]
            dictlike[title] = formes

        genders = {'masc': 0, 'femn': 1, 'neut': 2, None: 3}

        if word.tag.POS == 'GRND':
            if ', ' in dictlike["деепричастие"][0]:
                dictlike['деепричастие'] = dictlike['деепричастие'][0].split(', ')
            for form in dictlike['деепричастие']:
                if check(word.word, form):
                    return form
            return not_found
        if 'past' in word.tag:
            if word.tag.gender is None:
                res = dictlike['они'][1] 
            else: 
                res = past_gend[genders[word.tag.gender]]
            if not check(word.word, res):
                return not_found
            return res
        ind = 0
        res = ""
        if 'impr' in word.tag:
            ind = -1
            if 'plur' in word.tag:
                res = dictlike['вы'][-1]
            else:
                res = dictlike["ты"][-1]
        else:
            res = dictlike[present[(word.tag.person, word.tag.number)]][0]
        if check(word.word, res):
            return res
        else:
            return not_found
    else:
        print(need)
        if check(word.word, need):
            return need
        else:
            return not_found


class ProxyMaster:
    proxy_list = []
    last = 0
    ua = None

    def get_proxy(self):
        pass
        self.proxy_list = []
        url = 'https://www.sslproxies.org/'

        doc = rq.get(url, headers={'User-Agent': self.ua.random})

        soup = bs4.BeautifulSoup(doc.text, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            self.proxy_list.append({
              'ip':   row.find_all('td')[0].string,
              'port': row.find_all('td')[1].string
        })

    def __init__(self):
        self.last = 0
        self.ua = UserAgent()
        #self.get_proxy()

    def feed_with_proxy(self):
        elem = self.proxy_list[rd.randint(0, len(self.proxy_list) - 1)]
        proxy = 'https://' + elem['ip'] + ":" + elem['port']
        return {
            'http': proxy,
            'https': proxy
        }

    def get(self, url):
        if self.last % 100 == 0:
            pass
            #self.get_proxy()
        
        self.last += 1
        #resp = rq.get(url, headers={'User-Agent': self.ua.random})
        #if resp.status_code != 200:
        #    print("waited... ")
        #    sleep(120)
        #    resp = rq.get(url, )
        #pr = self.feed_with_proxy()
        ua = self.ua.random
        #print(pr, ua)
        #print(rq.get('http://icanhazip.com', headers={'User-Agent': ua}, proxies=pr).text)
        return rq.get(url, headers={'User-Agent': ua}, timeout=10)#, proxies=pr)

proxy = ProxyMaster()

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
    resp = proxy.get(url + normal)
    print("GOT", flush=True)
    print(resp.status_code, flush=True)
    #except:
    #    raise Exception("Timeout")
    if (resp.status_code != 200):
        raise Exception("Page not found")
    bs = bs4.BeautifulSoup(resp.text, 'html.parser')
    return get_essences(bs, normal)


class StressDB:
    articles = dict()

    def load(self, filename):
        with open(filename, encoding='utf-8') as file:
            articles = json.loads(file.read())
            #print(articles)
            self.articles = dict()
            for obj in articles:
                #print("objhashes:", obj)
                self.articles[obj] = dict()
                for el in articles[obj]:
                    #print(el)
                    if el == 'ADVB':
                        self.articles[obj][el] = articles[obj][el]
                        continue
                    #print(type(articles[obj]), len(articles[obj]))
                    #print(articles[obj])
                    #print(articles[obj][el])
                    self.articles[obj][el] = []
                    for i in range(len(articles[obj][el])):
                        self.articles[obj][el].append(bs4.BeautifulSoup(articles[obj][el][i], 'html.parser'))
            #print(self.articles)

    def __init__(self, source=None):
        self.articles = dict()
        if source is not None:
            self.load(source)

    def save(self, filename):
        jsonify = dict()
        for word in self.articles:
            if self.articles[word] is None:
                continue
            jsonify[word] = dict()
            for tag in self.articles[word]:
                if tag == 'ADVB':
                    jsonify[word][tag] = self.articles[word][tag]
                    continue

                arr = []
                #print(type(word), type(tag))
                #print(tag)
                for el in self.articles[word][tag]:
                    arr.append(str(el))
                jsonify[word][tag] = arr
        #print(jsonify)

        with open(filename, 'w') as file:
            print(json.dumps(jsonify), file=file)
        pass

    def get_stress(self, parse):
        objhash = parse.normal_form
        table = None
        if objhash not in self.articles:
            try:
                self.articles[objhash] = get_stress(parse)
            except Exception as exp:
                if exp.args[0] != 'Page not found' and exp.args[0] != 'Timeout':
                    raise
                #print(exp.args[0])
                self.articles[objhash] = None

        table = self.articles[objhash]
        print("find_formstress...", flush=True)
        form = find_formstress(parse, table)
        print("got it", flush=True)
        return form

    def __len__(self):
        return len(self.articles)


if __name__ == "__main__":
    import pymorphy2 as py
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
        for word in words:
            print("word:", word, flush=True)
            print(word, db.get_stress(morph.parse(word)[0]))
            if len(db) % 300 == 0:
                print(len(db))
                print("SAVED")
                db.save("db-stress-" + str(len(db)) + ".txt")
                db.save("stressdb.json")
                db = StressDB('stressdb.json')
                sleep(60)
                print("COMPLEATED")
                #break
    
    '''while True:
        word = input()
        if word == 'save':
            db.save(input())
        elif word == 'load':
            db.load(input())
        else:
            print(db.get_stress(morph.parse(word)[0]))'''