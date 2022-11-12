import spacy
import numpy as np
import pickle
import os

nlp = pickle.load(open(os.path.join('./nlp_md.pkl'), 'rb'))

# testing for threshold value
# words we want the model to report as similar
file = open('similar_words.txt', 'r')
similar_sims = []
line = file.readline()
while line != '':
    words = line.split(', ')
    first_word = nlp(words[0])
    sims = [first_word.similarity(nlp(x)) for x in words[1:]]
    similar_sims.append(sims)
    line = file.readline()
print(similar_sims)

