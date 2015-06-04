import string  
import re  
import sys
import os
from collections import *
from math import *
from numpy import array
import numpy as np


dimension = 400

def Transform(Vector_word, fileName, outputFile, flag):
    global dimension
    with open(fileName, 'r', encoding = 'utf-8') as fp:
        with open(outputFile, 'w', encoding = 'utf-8') as outFp:
            for lines in fp:
                words = lines[:-1].split()
                if len(words):
                    temp = np.zeros(dimension)
                    for word in words:
                        temp = np.add(temp,Vector_word[word])
                        # temp = temp + Vector_word[word]
                    temp = temp / float(dimension)
                    outFp.write(str(flag))
                    if len(temp) != dimension:
                        print("Vector error")
                        print(temp)
                    for x in range(0,dimension):
                        outFp.write(' ' + str(x + 1) + ':' + str(temp[x]))
                    outFp.write('\n')
                        

def ReadInVector(vector_file_name, Vector_word, Lexicon_Corpus):
    with open(vector_file_name, 'r', encoding = 'utf-8') as fp:
        for lines in fp:
            line = lines[:-1].split()
            word = line[0].split('/')[0]
            if word in Lexicon_Corpus:
                temp = array(line[1:])
                if len(temp) != 400:
                    print("error!")
                    print(len(temp))
                    temp = temp[1:]
                Vector_word[word] = temp.astype(np.float)


def GetAllWords(Lexicon, fileName):
    with open(fileName, 'r', encoding = 'utf-8') as fp:
        for lines in fp:
            line = lines[:-1]
            words = line.split()
            for word in words:
                Lexicon[word] += 1


def transform2vecDNN(argv):
    Vector_word = Counter()
    Lexicon_Corpus = Counter()
    Address = './'
    polarizationSet = {'positive', 'negative'}
    prefix_Set = {'context_'}
    posfix_Set = {'_testing.txt', '_training.txt'}
    for polar in polarizationSet:
        for prefix in prefix_Set:
            for posfix in posfix_Set:
                fileName = Address + prefix + polar + posfix
                GetAllWords(Lexicon_Corpus, fileName)
    vector_file_name = Address + '4300W.vectors.txt'
    ReadInVector(vector_file_name, Vector_word, Lexicon_Corpus)
    for polar in polarizationSet:
        for prefix in prefix_Set:
            for posfix in posfix_Set:
                flag = 0
                fileName = Address + prefix + polar + posfix
                outputFile = Address + 'experiment_' + polar + '_DNN_Glov' + posfix
                if polar == 'positive':
                    flag = 1
                Transform(Vector_word, fileName, outputFile, flag)


if __name__ == '__main__':
    transform2vecDNN(sys.argv[1:])