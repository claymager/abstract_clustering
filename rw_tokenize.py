#!/bin/python3
from pymongo import MongoClient
import re
import string

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
    text = re.sub("|".join(amino_acids_long), "AMINO_ACID", text)

    text = text.replace(r"p.?<", "PLessThan")
    #text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
    return text

