#!/bin/python3
from pymongo import MongoClient
import re
import string
from nltk.stem import SnowballStemmer
import nltk.corpus

def get_driver():
    client = MongoClient("localHost",27017)
    collection = client.retraction_watch
    return collection.retracted

def main():
    retracted = get_driver()
    abstract_exists = {"abstract":{"$exists":1}}
    for doc in retracted.find(abstract_exists):
        abstract = doc["abstract"]
        tokens = tokenize_sci(abstract)

amino_acids_long = ["alanine", "arginine", "asparagine", "aspartic acid",
        "aspartate", "cysteine", "glutamine", "glutamic acid", "glutamate",
        "histidine", "glycine", "isoleucine", "leucine", "lysine", "methionine",
        "phenylalanine", "proline", "serine", "threonine", "tryptophan",
        "tyrosine", "valine"]
amino_acid_codes = ["ala", "arg", "asn", "asp", "cys", "gln", "glu", "gly",
        "his", "ile", "leu", "lys", "met", "phe", "pro", "ser", "thr", "trp",
        "tyr", "val"]

def clean( text ):
    text = text.lower()
    text = re.sub(r"\d\d?\.?\d*%", r"rwPERCENT", text)
    text = re.sub(r"p\s?<\s?0\.(\d*)", r"rwPLessThan\1", text)

    text = re.sub("[%s]" % re.escape(string.punctuation), " ", text)
    text = re.sub(r"–", r" ", text)
    text = re.sub(r"\b(19\d\d|20\d\d)\b", r"rwYEAR", text)
    text = re.sub(r"\b\d+\.?\d*\b", r"rwNUM", text)
    text = re.sub(r"\s", " ", text)

    stopwords = nltk.corpus.stopwords.words() + ["rwNUM","fig","figure"]

    #stem = SnowballStemmer("english").stem
    stem = stupid_stemmer

    stemmed = [ (word) #stemmer(word)
            for word in text.split(" ")
            if word not in stopwords ]
    return " ".join(stemmed)

def stupid_stemmer( word ):
    return re.sub(r"[sd]$", "", word)
