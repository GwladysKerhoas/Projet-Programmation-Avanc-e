#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 16:04:49 2021

@author: gwladyskerhoas
"""

################################## Déclaration des classes ##################################

import datetime as dt
import pickle
import itertools
import re
import pandas
import math
from gensim.summarization.summarizer import summarize
import nltk
from nltk.corpus import stopwords  
from nltk.tokenize import word_tokenize  
from nltk.tokenize import RegexpTokenizer




# Classe Corpus
class Corpus():
    
    def __init__(self,name):
        self.name = name
        self.collection = {}
        self.authors = {}
        self.id2doc = {}
        self.id2aut = {}
        self.ndoc = 0
        self.naut = 0
        self.chainereunie = ""
        self.dico = []
            
    def add_doc(self, doc):
        
        self.collection[self.ndoc] = doc
        self.id2doc[self.ndoc] = doc.get_title()
        self.ndoc += 1
        aut_name = doc.get_author()
        aut = self.get_aut2id(aut_name)
        if aut is not None:
            self.authors[aut].add(doc)
        else:
            self.add_aut(aut_name,doc)
            
    def add_aut(self, aut_name,doc):
        
        aut_temp = Author(aut_name)
        aut_temp.add(doc)
        
        self.authors[self.naut] = aut_temp
        self.id2aut[self.naut] = aut_name
        
        self.naut += 1

    def get_aut2id(self, author_name):
        aut2id = {v: k for k, v in self.id2aut.items()}
        heidi = aut2id.get(author_name)
        return heidi

    def get_doc(self, i):
        return self.collection[i]
    
    def get_coll(self):
        return self.collection

    def __str__(self):
        return "Corpus: " + self.name + ", Number of docs: "+ str(self.ndoc)+ ", Number of authors: "+ str(self.naut)
    
    def __repr__(self):
        return self.name

    def sort_title(self,nreturn=None):
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_title())][:(nreturn)]

    def sort_date(self,nreturn):
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_date(), reverse=True)][:(nreturn)]
    
    def save(self,file):
            pickle.dump(self, open(file, "wb" ))
            
    def reunion_chaine(self):
        if (self.chainereunie == ""):
            for doc in self.collection:
                chaine = self.collection[doc].get_text()
                self.chainereunie += (chaine)
            
    def search(self, keyword):
            sample = ""
            self.reunion_chaine() 
            if keyword in self.chainereunie:
               for m in re.finditer(keyword, self.chainereunie):
                   for i in range(m.start(0) - 50, m.end(0) + 50):
                       sample += self.chainereunie[i]
            print(sample)
                               
    def concorde(self, keyword, taille):
            sample = ""
            if keyword in self.chainereunie:
               for m in re.finditer(keyword, self.chainereunie):
                   for i in range(m.start(0) - taille, m.end(0) + taille):
                       sample += self.chainereunie[i]
            print(sample)
        
    def tokenize(self):
        
        # Récupération des stopwords de la langue anglaise
        stop_words = set(stopwords.words('english'))  
        tokenizer = RegexpTokenizer(r'\w+')
        
        chaineinter = ""
        
        for word in tokenizer.tokenize(self.chainereunie):
            chaineinter = chaineinter + word + " "
    
        word_tokens = word_tokenize(chaineinter)
  
        filtered_sentence = [w for w in word_tokens if not w in stop_words]  
  
        filtered_sentence = [] 
        
        # On ajoute à notre liste les mots non présent dans la liste de stopwords
        for w in word_tokens:  
            if w not in stop_words:  
                filtered_sentence.append(w)
        
        return filtered_sentence
        
    def stats(self):
        self.reunion_chaine()
        self.nettoyer_texte()

        # On sépare la chaine par mots
        if len(self.dico) == 0:
            self.dico = self.chainereunie.split(" ")
            self.dico = self.tokenize()
            dicsansboucl = list(set(self.dico))
            data = pandas.DataFrame.from_dict(self.dico)
            
            # On récupère la fréquence des mots avec value_counts()
            freq = data[0].value_counts()
            print("Les dix termes les plus utilisés :")
            print(freq.head(10))
        
    def nettoyer_texte(self):
        self.chainereunie = self.chainereunie.lower()
        self.chainereunie.replace("\n"," ")
        
        
       
# Classe Author
class Author():
    def __init__(self,name):
        self.name = name
        self.production = {}
        self.ndoc = 0
        
    def add(self, doc):     
        self.production[self.ndoc] = doc
        self.ndoc += 1

    def __str__(self):
        return "Auteur: " + self.name + ", Number of docs: "+ str(self.ndoc)
    def __repr__(self):
        return self.name
    

# Classe mère permettant de modéliser un Document (au sens large)
class Document():
    
    # constructor
    def __init__(self, date, title, author, text, url):
        self.date = date
        self.title = title
        self.author = author
        self.text = text
        self.url = url
    
    # getters
    
    def get_author(self):
        return self.author

    def get_title(self):
        return self.title
    
    def get_date(self):
        return self.date
    
    def get_source(self):
        return self.source
        
    def get_text(self):
        return self.text

    def __str__(self):
        return "Document " + self.getType() + " : " + self.title
    
    def __repr__(self):
        return self.title

    def sumup(self,ratio):
        try:
            auto_sum = summarize(self.text,ratio=ratio,split=True)
            out = " ".join(auto_sum)
        except:
            out =self.title            
        return out
    
    def getType(self):
        pass
    
# Classe fille permettant de modéliser un Document Reddit
class RedditDocument(Document):
    
    def __init__(self, date, title,
                 author, text, url, num_comments):        
        Document.__init__(self, date, title, author, text, url)
        # ou : super(...)
        self.num_comments = num_comments
        self.source = "Reddit"
        
    def get_num_comments(self):
        return self.num_comments

    def getType(self):
        return "reddit"
    
    def __str__(self):
        #return(super().__str__(self) + " [" + self.num_comments + " commentaires]")
        return Document.__str__(self) + " [" + str(self.num_comments) + " commentaires]"
    

# Classe fille permettant de modéliser un Document Arxiv
class ArxivDocument(Document):
    
    def __init__(self, date, title, author, text, url, coauteurs):
        #datet = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        Document.__init__(self, date, title, author, text, url)
        self.coauteurs = coauteurs
    
    def get_num_coauteurs(self):
        if self.coauteurs is None:
            return(0)
        return(len(self.coauteurs) - 1)

    def get_coauteurs(self):
        if self.coauteurs is None:
            return([])
        return(self.coauteurs)
        
    def getType(self):
        return "arxiv"

    def __str__(self):
        s = Document.__str__(self)
        if self.get_num_coauteurs() > 0:
            return s + " [" + str(self.get_num_coauteurs()) + " co-auteurs]"
        return s
    













