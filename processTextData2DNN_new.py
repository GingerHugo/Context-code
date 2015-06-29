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
# StopWord_set = set()
LongSentenceNumber = 0
NumberOfLine = 0
TotalLength = 0
entryList = defaultdict(lambda: defaultdict(list))
SentenceThreshold = 60

def CNNFeatureVectorBuilding(InputAddress, training, polar, posfix, Vocabulary, cv=10, ConvolLengh = 6, max_l = 60,flag = True, Documentflag = False):
        # global  Marker_set, StopWord_set
        global  Marker_set
        if polar == 'positive':
                label = 1
        else:
                label = 0
        # print("Processing {} file".format(InputAddress))
        # print('Documentflag: {}'.format(Documentflag))
        BlackList = set()
        if Documentflag:
                BlackListAddress = './Entry_processed/DeleteList'
                BlackListName = '{}/Entry_{}_{}.txt'.format(BlackListAddress, polar, posfix)
                # print("BlackList file Name {}".format(BlackListName))
                ReadInBlackList(BlackList, BlackListName)
                # print(BlackList)
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                currentLine = 0
                for lines in fp:
                        result = []
                        if (currentLine in BlackList):
                                if Documentflag:
                                        currentLine += 1
                                        continue
                        for x in range(0,ConvolLengh - 1):
                                result.append(0)
                        line = lines[:-1]
                        sentence = GetSentence(line, flag)
                        for word in sentence.split():
                                candidate = GetCandiate(word, flag)
                                # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                if  (candidate not in Marker_set):
                                        result.append(Vocabulary[candidate])
                        if len(result) > max_l + (ConvolLengh - 1):
                                print("LongErrorCase")
                                print(currentLine)
                        while len(result) < (max_l + 2*(ConvolLengh - 1)):
                                result.append(0)
                        vector = np.array(result, dtype="int")
                        # datum  = {"y": label,
                        #                   "vector": vector,
                        #                   "split": np.random.randint(0,cv)}
                        datum = [label, vector, np.random.randint(0,cv)]
                        training.append(datum)
                        currentLine += 1

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
                # print(W[Vocabulary[word]])
                i += 1
        return W

def outputWordVector(W, outputLexiconAddress):
        np.savetxt(outputLexiconAddress, W)

def outputFeatureFile(vectorList, outputFeatureAddress):
        # with open(outputFeatureAddress, 'w', encoding = 'utf-8') as fp:
        result = []
        labelSet = {1, 0}
        for member in vectorList:
                if (member[0] not in labelSet) or member[1].shape[0] != 70:
                        print("Error")
                        print(member[1])
                        print(member[1].shape)
                        print(member[0])
                result.append(np.concatenate((member[1], (np.array([member[0]], dtype = 'int')))))
        result = np.array(result, dtype = 'int')
        np.savetxt(outputFeatureAddress, result, fmt='%i',)

def CNNFeatureExtraction(args):
        global LongSentenceNumber, NumberOfLine, TotalLength
        path = './Entry_processed/connectives.csv'
        ReadInReverseDiscourseMarker(Marker_set, path)
        StopWord_set = set()
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        Vocabulary = {}
        fileAddress = {('/rule-based/', 'naive_'), ('/discourse/', 'discourse_')}
        polarSet = ['positive', 'negative']
        # TypeSet = {'_automatic_', '_manual_corrected_'}
        TypeSet = {'_automatic_'}
        CrossType = {'training'}
        prefixList = ['Context_', 'Comment_']
        preposfix = args.model + '_Feature_'
        postfix = '.txt'
        output_document = 'CNN_Feature_Py'
        address2 = './Entry_processed/Comment_Extracted'
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress, prefixList)
        IDFDict = Counter()
        for tuples in combinations:
                if tuples[4].startswith('Context'):
                        GetWordCollection(Lexicon_Corpus, IDFDict,args.file_path.replace('\\','/') + tuples[3][0] + tuples[4] + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
                else:
                        GetWordCollection(Lexicon_Corpus, IDFDict, address2 + tuples[3][0] + tuples[4] + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
        GetWordCollection(Lexicon_Corpus, IDFDict, args.file_path.replace('\\','/') + '/discourse/Context_discourse_positive_automatic_testing.txt', Marker_set, StopWord_set)
        GetWordCollection(Lexicon_Corpus, IDFDict, args.file_path.replace('\\','/') + '/discourse/Context_discourse_negative_automatic_testing.txt', Marker_set, StopWord_set)
        CalculateVocabularySequence(Vocabulary, Lexicon_Corpus)
        OOVWord = ReadInVector(args.voc_path, Vector_word, Lexicon_Corpus, args.model)
        AddOOVVectors(Vector_word, Lexicon_Corpus, OOVWord, min_df=1, k=400)
        W = transformWordVector(Vector_word, Vocabulary, 400)
        outputLexiconAddress = "{}/{}/New_{}lexicon.txt".format(args.file_path.replace('\\','/')[:-18], output_document, preposfix)
        outputWordVector(W, outputLexiconAddress)
        # Clause Training part
        for methodType in fileAddress:
                training = []
                for lexiconType in TypeSet:
                        for prefix in prefixList:
                                for polar in polarSet:
                                        for crossLabel in CrossType:
                                                if prefix.startswith('Context'):
                                                        InputAddress = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1] + polar + lexiconType + crossLabel + postfix
                                                else:
                                                        InputAddress = address2 + methodType[0] + prefix + methodType[1] + polar + lexiconType + crossLabel + postfix
                                                CNNFeatureVectorBuilding(InputAddress, training, polar, crossLabel, Vocabulary, 10, 6, 60, True)
                outputFeatureAddress = "{}/{}/New_Clause_{}{}training.txt".format(args.file_path.replace('\\','/')[:-18], output_document, methodType[1], preposfix)
                outputFeatureFile(training, outputFeatureAddress)
                print (methodType[1][:-1], " training dataset created!")

        # Entry Part and Test Entry
        print ("Creating Testing dataset!")
        Testing = []
        for polar in polarSet:
                InputAddress = args.file_path.replace('\\','/') + '/discourse/Context_discourse_{}_automatic_testing.txt'.format(polar)
                CNNFeatureVectorBuilding(InputAddress, Testing, polar, 'testing', Vocabulary, 10, 6, 60, True)
        outputFeatureAddress = "{}/{}/New_Clause_{}testing.txt".format(args.file_path.replace('\\','/')[:-18], output_document, preposfix)
        outputFeatureFile(Testing, outputFeatureAddress)
        print ("Both training and testing dataset created!")

if __name__=="__main__":
        args = process_commands()
        CNNFeatureExtraction(args)        