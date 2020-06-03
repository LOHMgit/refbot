# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:44:52 2018

@author: LOHM
"""
import re
import os
import json
import requests
from fuzzywuzzy import fuzz

class BQutils:
    """
        Bible Quran Utility class which finds Bible and Quranic verses
        and gets them through a Bible and Quran API
        Need a valid ESV token to use the ESV API
    """

    def __init__(self, threshold = 70):
        self.bob = json.load(open('books_of_the_bible.json', 'r'))
        self.threshold = threshold
        #second token for emdc demo only
        self.esv_token = os.environ.get('ESV_TOKEN', None)

    def find_bible_verses(self, text):
        """
        Finds Bible verse references in text
        """
        refs = []
        #regex that finds (1) Peter 1:3(-10)  (bracketed items are optional)
        regex = re.compile(r'(\d?\s?\w+.?)\s(\d+\s?)[:;](\s?\d+-?\d?\d?\d?)')
        matchs = regex.findall(text)
        if matchs:
            for match in matchs:
                #chapter and verse are easy and common to both fuzzy books and aliases
                chapresult = match[1].strip()
                verseresult = match[2].strip()
                #does a fuzzy match on nearest Biblical book above the threshold ratio
                bresult = [(idx, fuzz.ratio(match[0].strip(), b['name']))\
                           for idx, b in enumerate(self.bob) if \
                           fuzz.ratio(match[0].strip(), b['name']) >= self.threshold]
                #if our matches are Biblical books
                if bresult:
                    #choose the best book match
                    maxdx = max(bresult, key=lambda tup: tup[1])
                    bookresult = self.bob[maxdx[0]]['name']
                    #bundle the book, chapter and verse results
                    refs.append((bookresult, chapresult, verseresult))
                else:
                    #let's see if an alias was typed - the rstrip('.') covers the case of a period
                    aliasresult = [b['name'] for b in self.bob\
                                   if match[0].rstrip('.').strip() in ' '.join(b['aliases'])]
                    if aliasresult:
                        refs.append((aliasresult[0], chapresult, verseresult))
            return refs

    def get_scripture(self, ref):
        """
        Uses the ESV api to get the scriptural quote
        """
        headers = {'Accept': 'application/json',
                   'Authorization': 'Token '+ self.esv_token,
                  }
        params = (('q', ref)),
        response = requests.get('https://api.esv.org/v3/passage/text/',
                                headers=headers, params=params)
        return response.json()

    @staticmethod
    def find_quran_verses(text):
        """
        Finds potential references to the Quran in text
        """
        #regex1 finds all references 11:197 or 11:197-199
        regex1 = re.compile(r'([Qq]ur\'?an)?\s?(\d{1,3}\s?)[:;](\s?\d{1,3}-?\d?\d?\d?)')
        match = regex1.search(text)
        if match:
            allqrefs = regex1.findall(text)
            if allqrefs:
                qrefs = list([(cv[1], cv[2]) for cv in allqrefs])
                return qrefs
        return None

    @staticmethod
    def get_quran(qref):
        """
        Uses the Qurancloud api to get the Quranic quote
        """
        try:
            sura = qref[0]
            ayah = qref[1]
        except IndexError as i_error:
            print('Incomplete Quranic reference' + qref)
            print(i_error)
            return ''
        qurl = 'http://api.alquran.cloud/ayah/'
        response = requests.get(qurl + sura + ':' + ayah + '/en.asad')
        return response.json()
