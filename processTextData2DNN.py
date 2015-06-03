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

def CNNFeatureVectorBuilding(InputAddress, training, polar, posfix, Vocabulary, cv=10, ConvolLengh = 6, max_l = 60,flag = True, Documentflag = False):
        global  Marker_set, StopWord_set
        if polar == 'positive':
                label = 1
        else:
                label = 0
        BlackListAddress = './Entry_processed/DeleteList'
        BlackListName = '{}/Entry_{}_{}.txt'.format(BlackListAddress, polar, posfix)
        BlackList = set()
        if Documentflag:
                ReadInBlackList(BlackList, BlackListName)
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                currentLine = 0
                for lines in fp:
                        result = []
                        for x in range(0,ConvolLengh - 1):
                                result.append(0)
                        if (currentLine in BlackList) and Documentflag:
                                currentLine += 1
                                continue
                        currentLine += 1
                        Documentflag
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
                        # datum  = {"y": label,
                        #                   "vector": vector,
                        #                   "split": np.random.randint(0,cv)}
                        datum = [label, vector, np.random.randint(0,cv)]
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
                # print(W[Vocabulary[word]])
                i += 1
        return W

def outputWordVector(W, outputLexiconAddress):
        np.savetxt(outputLexiconAddress, W)
        # with open(outputLexiconAddress, 'w', encoding = 'utf-8') as fp:
        #         for x in range(0, W.shape[0]):
        #                 # print(W[x])
        #                 fp.write(str(W[x]))
        #                 fp.write('\n')

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
        ReadInDiscourseMarker(Marker_set, path)
        path = './Entry_processed/BaiduStopwords.txt'
        ReadInStopWord(StopWord_set, path)
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        Vocabulary = {}
        fileAddress = {('/rule-based/', 'naive_'), ('/discourse/', 'discourse_')}
        polarSet = ['positive', 'negative']
        TypeSet = {'_automatic_', '_manual_corrected_'}
        CrossType = {'training', 'testing'}
        prefix = 'Context_'
        preposfix = args.model + '_Feature_'
        postfix = '.txt'
        output_document = 'CNN_Feature_Py'
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress)
        IDFDict = Counter()
        for tuples in combinations:
                GetWordCollection(Lexicon_Corpus, IDFDict,args.file_path.replace('\\','/') + tuples[3][0] + prefix + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
        EntryAddress = './Entry_processed/Entry_segmented'
        combinations = itertools.product(polarSet, CrossType)
        for tuples in combinations:
                EntryfileName = '{}/Segmented_Entry_{}_{}.txt'.format(EntryAddress, tuples[0], tuples[1])
                GetWordCollection(Lexicon_Corpus, IDFDict, EntryfileName, Marker_set, StopWord_set, False)
        CalculateVocabularySequence(Vocabulary, Lexicon_Corpus)
        OOVWord = ReadInVector(args.voc_path, Vector_word, Lexicon_Corpus, args.model)
        AddOOVVectors(Vector_word, Lexicon_Corpus, OOVWord, min_df=1, k=400)
        textPrefix = 'Context_Entire_Doc_'
        textPosfix = '_testing.txt'
        # print((Vector_word['亚州']).shape)
        # print((Vector_word['亚州']))
        W = transformWordVector(Vector_word, Vocabulary, 400)
        # print(W[1].shape)
        # a = n / m
        outputLexiconAddress = "{}/{}/lexicon.txt".format(args.file_path.replace('\\','/')[:-18], output_document)
        outputWordVector(W, outputLexiconAddress)
        # Context part
        for lexiconType in TypeSet:
                for methodType in fileAddress:
                        training = []
                        testing = []
                        # training_P = []
                        # training_N = []
                        for polar in polarSet:
                                for crossLabel in CrossType:
                                        InputAddress = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1] + polar + lexiconType + crossLabel + postfix
                                        if crossLabel == 'training':
                                                # if polar == 'positive':
                                                #         CNNFeatureVectorBuilding(InputAddress, training, polar, Vocabulary, 10, 6, 60, True)
                                                # else:
                                                CNNFeatureVectorBuilding(InputAddress, training, polar, crossLabel, Vocabulary, 10, 6, 60, True)
                                        else:
                                                CNNFeatureVectorBuilding(InputAddress, testing, polar, crossLabel, Vocabulary, 1, 6, 60, True)                                
                        # dumpFileName = "{}/{}/{}{}{}package.p".format(args.file_path.replace('\\','/')[:-18], output_document, methodType[0][1:], methodType[1], lexiconType[1:])
                        # print(dumpFileName)
                        # pickle.dump([W, training, testing, testingEntry], open(dumpFileName, "wb"), protocol=2)
                        outputFeatureAddress = "{}/{}/{}{}{}training.txt".format(args.file_path.replace('\\','/')[:-18], output_document, methodType[0][1:], methodType[1], lexiconType[1:])
                        outputFeatureFile(training, outputFeatureAddress)
                        outputFeatureAddress = "{}/{}/{}{}{}testing.txt".format(args.file_path.replace('\\','/')[:-18], output_document, methodType[0][1:], methodType[1], lexiconType[1:])
                        outputFeatureFile(testing, outputFeatureAddress)
                        print (lexiconType, methodType[1], " dataset created!")

        # Entry Part and Test Entry
        print ("Creating Entry and Document dataset!")
        testingEntry = []
        trainingDocument = []
        testingDocument = []
        EntryAddress = './Entry_processed/Entry_segmented'
        for polar in polarSet:
                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix + polar + textPosfix
                CNNFeatureVectorBuilding(InputAddress, testingEntry, polar, 'testingEntry', Vocabulary, 1, 6, 60, False)
                EntryfileName = '{}/Segmented_Entry_{}_training.txt'.format(EntryAddress, tuples[0], tuples[1])
                CNNFeatureVectorBuilding(InputAddress, trainingDocument, polar, 'training', Vocabulary, 1, 6, 60, False, True)
                EntryfileName = '{}/Segmented_Entry_{}_testing.txt'.format(EntryAddress, tuples[0], tuples[1])    
                CNNFeatureVectorBuilding(InputAddress, testingDocument, polar, 'testing', Vocabulary, 1, 6, 60, False, True)
        outputFeatureAddress = "{}/{}/testingEntry.txt".format(args.file_path.replace('\\','/')[:-18], output_document)
        outputFeatureFile(testingEntry, outputFeatureAddress)
        outputFeatureAddress = "{}/{}/trainingDocument.txt".format(args.file_path.replace('\\','/')[:-18], output_document)
        outputFeatureFile(trainingDocument, outputFeatureAddress)
        outputFeatureAddress = "{}/{}/testingDocument.txt".format(args.file_path.replace('\\','/')[:-18], output_document)
        outputFeatureFile(testingDocument, outputFeatureAddress)
        print ("Entry Part and Test Entry dataset created!")

if __name__=="__main__":
        args = process_commands()
        CNNFeatureExtraction(args)        