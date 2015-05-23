# convert from inverted_index to doc features
import argparse
from collections import defaultdict
import numpy as np
import sys, re
import pandas as pd
from commonDiscourseMarker import *
from commonIO import *
import itertools
from commonVecTransform import *
from processTextDataCheck import *
import math
import pickle

def process_commands():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('file_path')
        parser.add_argument('voc_path')
        parser.add_argument('-model', action='store', default='Glove')
        # parser.add_argument('-output', action='store_true', default=False)
        # parser.add_argument('-discourse', action='store_true', default=False)
        return parser.parse_args()

Marker_set = set()
StopWord_set = set()
LongSentenceNumber = 0
NumberOfLine = 0
TotalLength = 0
entryList = defaultdict(lambda: defaultdict(list))
SentenceThreshold = 60

def CNNFeatureVectorBuilding(InputAddress, training, polar, cv=10, Vocabulary, ConvolLengh = 6, max_l = 60,flag = True):
        global  Marker_set, StopWord_set
        if polar == 'positive':
                label = 1
        else:
                label = 0
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        result = []
                        for x in range(0,ConvolLengh - 1):
                                result.append(0)
                        line = lines[:-1]
                        sentence = GetSentence(line, flag)
                        for word in sentence.split():
                                candidate = GetCandiate(word, flag)
                                if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                        result.append(Vocabulary[candidate])
                        if len(result) > max_l + (ConvolLengh - 1):
                                print("LongErrorCase")
                        while len(result) < (max_l + 2*(ConvolLengh - 1)):
                                result.append(0)
                        vector = np.array(result, dtype="int")
                        datum  = {"y": label,
                                          "vector": vector,
                                          "split": np.random.randint(0,cv)}
                        training.append(datum)

def transformWordVector(Vector_word, Vocabulary, dimension = 400):
        """
        Get word matrix. W[i] is the vector for word indexed by i
        """
        vocab_size = len(Vector_word)
        W = np.zeros(shape=(vocab_size+1, dimension))            
        W[0] = np.zeros(dimension)
        i = 1
        for word in Vector_word:
                W[Vocabulary[word]] = Vector_word[word].astype(np.float32, copy=False)
                i += 1
        return W

def CNNFeatureExtraction(args):
        global LongSentenceNumber, NumberOfLine, TotalLength
        path = './Entry_processed/connectives.csv'
        ReadInDiscourseMarker(Marker_set, path)
        path = './Entry_processed/BaiduStopwords.txt'
        ReadInStopWord(StopWord_set, path)
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        Vocabulary = {}
        fileAddress = {('/rule-based/', 'naive_'), ('/discourse/', 'discourse_')}
        polarSet = {'positive', 'negative'}
        TypeSet = {'_automatic_', '_manual_corrected_'}
        CrossType = {'training', 'testing'}
        prefix = 'Context_'
        preposfix = args.model + '_Feature_'
        postfix = '.txt'
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress)
        for tuples in combinations:
                GetWordCollection(Lexicon_Corpus, IDFDict,args.file_path.replace('\\','/') + tuples[3][0] + prefix + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
        CalculateVocabularySequence(Vocabulary, Lexicon_Corpus)
        OOVWord = ReadInVector(args.voc_path, Vector_word, Lexicon_Corpus)
        AddOOVVectors(Vector_word, Lexicon_Corpus, OOVWord, min_df=1, k=400)
        textPrefix = 'Context_Entire_Doc_'
        textPosfix = '_testing.txt'
        W = transformWordVector(Vector_word, Vocabulary, 400)
        for lexiconType in TypeSet:
                for methodType in fileAddress:
                        training = []
                        testing = []
                        testingEntry = []
                        # training_P = []
                        # training_N = []
                        for polar in polarSet:
                                for crossLabel in CrossType:
                                        InputAddress = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1] + polar + lexiconType + crossLabel + postfix
                                        if crossLabel == 'training':
                                                if polar == 'positive':
                                                        CNNFeatureVectorBuilding(InputAddress, training, polar, 10, Vocabulary, 6, 60, True)
                                                else:
                                                        CNNFeatureVectorBuilding(InputAddress, training, polar, 10, Vocabulary, 6, 60, True)
                                        else:
                                                CNNFeatureVectorBuilding(InputAddress, testing, polar, 1, Vocabulary, 6, 60, True)
                                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix + polar + textPosfix         
                                CNNFeatureVectorBuilding(InputAddress, testingEntry, polar, 1, Vocabulary, 6, 60, False)
                                pickle.dump([W, training, testing, testingEntry], open("mr.p", "wb"))
                                print (lexiconType, methodType[1], " dataset created!")

if __name__=="__main__":
        args = process_commands()
        CNNFeatureExtraction(args)        