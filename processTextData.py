# convert from inverted_index to doc features
import argparse
from collections import defaultdict
import numpy as np
import sys, re
# import pandas as pd
from commonDiscourseMarker import *
from commonIO import *
import itertools
from commonVecTransform import *
from processTextDataCheck import *
import math

def process_commands():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('file_path')
        parser.add_argument('voc_path')
        parser.add_argument('-model', action='store', default='Glove')
        parser.add_argument('-output', action='store_true', default=False)
        parser.add_argument('-discourse', action='store_true', default=False)
        return parser.parse_args()

Marker_set = set()
StopWord_set = set()
LongSentenceNumber = 0
NumberOfLine = 0
TotalLength = 0
entryList = defaultdict(lambda: defaultdict(list))
SentenceThreshold = 60

def GetLabel(polar):
        if polar == 'positive':
                return 1
        else:
                return 0

def outputCNNExtractedFeatures(InputAddress, OutputAddress, polar, continueFlag, Vector_word, MaxLength = 60, ConvolLengh = 6, dimension = 400, flag = True):
        global  Marker_set, StopWord_set
        label = GetLabel(polar)
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                if continueFlag:
                        fp2 = open(OutputAddress, 'a', encoding = 'utf-8')
                else:
                        fp2 = open(OutputAddress, 'w', encoding = 'utf-8')
                        for lines in fp:
                                fp2.write(str(label))
                                Initial = ConvolLengh
                                line = lines[:-1]
                                sentence = GetSentence(line, flag)
                                for word in sentence.split():
                                        candidate = GetCandiate(word, flag)
                                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                vector = Vector_word[candidate]
                                                outputString = ''
                                                for x in range(0, dimension):
                                                        outputString += ' {}:{}'.format((((Initial - 1) * dimension + 1) + x), vector[x])
                                                Initial += 1
                                                fp2.write(outputString)
                                fp2.write('\n')
                fp2.close()

def outputVectorSumExtractedFeatures(InputAddress, OutputAddress, polar, continueFlag, Vector_word, dimension = 400, flag = True):
        global  Marker_set, StopWord_set
        label = GetLabel(polar)
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                if continueFlag:
                        fp2 = open(OutputAddress, 'a', encoding = 'utf-8')
                else:
                        fp2 = open(OutputAddress, 'w', encoding = 'utf-8')
                        for lines in fp:
                                fp2.write(str(label))
                                line = lines[:-1]
                                sentence = GetSentence(line, flag)
                                vector = np.zeros(dimension, 'float')
                                for word in sentence.split():
                                        candidate = GetCandiate(word, flag)
                                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                vector = vector + Vector_word[candidate]
                                outputString = ''
                                for x in range(0, dimension):
                                        outputString += ' {}:{}'.format((1 + x), vector[x])
                                fp2.write(outputString + '\n')
                fp2.close()

def outputTFIDFExtractedFeatures(InputAddress, OutputAddress, polar, continueFlag, IDFDict, N, Vocabulary, flag = True):
        global  Marker_set, StopWord_set
        label = GetLabel(polar)
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                if continueFlag:
                        fp2 = open(OutputAddress, 'a', encoding = 'utf-8')
                else:
                        fp2 = open(OutputAddress, 'w', encoding = 'utf-8')
                        for lines in fp:
                                fp2.write(str(label))
                                line = lines[:-1]
                                sentence = GetSentence(line, flag)
                                TF = Counter()
                                for word in sentence.split():
                                        candidate = GetCandiate(word, flag)
                                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                TF[candidate] += 1
                                value = defaultdict(float)
                                for word in TF:
                                        if IDFDict[word] == 0:
                                                print("IDF Zero Case", word)
                                                continue
                                        value[Vocabulary[word]] = round(float(TF[word]) * math.log(float(N) / float(IDFDict[word])), 10)
                                vector = OrderedDict(sorted(value.items(), key=lambda t: t[0]))
                                outputString = ''
                                for index in vector:
                                        outputString += ' {}:{}'.format((index), vector[index])
                                fp2.write(outputString + '\n')
                fp2.close()

def GetTotalN(InputAddress, IDFDict, flag = True):
        global Marker_set, StopWord_set
        count = 0
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        count += 1
                        line = lines[:-1]
                        sentence = GetSentence(line, flag)
                        wordBags = set()
                        for word in sentence.split():
                                candidate = GetCandiate(word, flag)
                                if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                        wordBags.add(candidate)
                        for word in wordBags:
                                IDFDict[word] += 1
        return count

def featureExtraction(args):
        global Marker_set, StopWord_set
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        IDFDict = Counter()
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
        CalculateVocabularySequence(Vocabulary, IDFDict)
        OOVWord = ReadInVector(args.voc_path, Vector_word, Lexicon_Corpus, args.model)
        AddOOVVectors(Vector_word, Lexicon_Corpus, OOVWord, min_df=1, k=400)
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress)
        fileBags = set()
        for tuples in combinations:
                InputAddress = args.file_path.replace('\\','/') + tuples[3][0] + prefix + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix
                if (tuples[1],tuples[2],tuples[3]) not in fileBags:
                        fileBags.add((tuples[1],tuples[2],tuples[3]))
                        continueFlag = 0
                else:
                        continueFlag = 1
                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/CNN_feature/' + tuples[3][0] + preposfix + tuples[3][1] + tuples[1][1:] + tuples[2] + postfix
                outputCNNExtractedFeatures(InputAddress, OutputAddress, tuples[0], continueFlag, Vector_word, 60, 6, 400, True)
                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/wordVector_feature/' + tuples[3][0] + preposfix + tuples[3][1] + tuples[1][1:] + tuples[2] + postfix
                outputVectorSumExtractedFeatures(InputAddress, OutputAddress, tuples[0], continueFlag, Vector_word, 400, True)
        textPrefix = 'Context_Entire_Doc_'
        textPosfix = '_testing.txt'
        for lexiconType in TypeSet:
                for methodType in fileAddress:
                        combinations = itertools.product(polarSet, CrossType)
                        N = 0
                        IDFDict = Counter()
                        for tuples in combinations:
                                InputAddress = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1] + tuples[0] + lexiconType + tuples[1] + postfix
                                N += GetTotalN(InputAddress, IDFDict, True)
                        combinations = itertools.product(polarSet, CrossType)
                        fileBags = set()
                        for tuples in combinations:
                                if (tuples[1]) not in fileBags:
                                        fileBags.add(tuples[1])
                                        continueFlag = 0
                                else:
                                        continueFlag = 1
                                InputAddress = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1] + tuples[0] + lexiconType + tuples[1] + postfix
                                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + methodType[0] + preposfix + methodType[1] + tuples[0] + lexiconType + tuples[1] + postfix
                                outputTFIDFExtractedFeatures(InputAddress, OutputAddress, tuples[0], continueFlag, IDFDict, N, Vocabulary, True)
                        N = 0
                        IDFDict = Counter()
                        for polar in polarSet:
                                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix + polar + textPosfix
                                N += GetTotalN(InputAddress, IDFDict, False)
                        continueFlag = 0
                        for polar in polarSet:
                                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix + polar + textPosfix
                                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/CNN_feature/' + methodType[0] + preposfix + methodType[1] + polar + lexiconType + 'TestEntry' + postfix
                                outputCNNExtractedFeatures(InputAddress, OutputAddress,  polar, continueFlag, Vector_word, 60, 6, 400, False)
                                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/wordVector_feature/' + methodType[0] + preposfix + methodType[1] + polar + lexiconType + 'TestEntry' + postfix
                                outputVectorSumExtractedFeatures(InputAddress, OutputAddress, polar, continueFlag, Vector_word, 400, False)
                                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + methodType[0] + preposfix + methodType[1] + polar + lexiconType + 'TestEntry' + postfix
                                outputTFIDFExtractedFeatures(InputAddress, OutputAddress, polar, continueFlag, IDFDict, N, Vocabulary, False)
                                continueFlag = 1


def processTextData(args):
        global LongSentenceNumber, NumberOfLine, TotalLength
        # negator_set = set()
        path = './Entry_processed/connectives.csv'
        ReadInDiscourseMarker(Marker_set, path)
        path = './Entry_processed/BaiduStopwords.txt'
        ReadInStopWord(StopWord_set, path)
        # fileList = []
        if args.output:
                featureExtraction(args)
        else:
                if args.discourse:
                        fileName = '/discourse/'
                        character = 'discourse_'
                else:
                        fileName = '/rule-based/'
                        character = 'naive_'
                MaxLength = 0
                fileList = TraverseFileName(fileName, character)
                # print(args.file_path.replace('\\','/'))
                for textFile in fileList:
                        # print(textFile)
                        with open(args.file_path.replace('\\','/') + textFile, 'r', encoding = 'utf-8') as fp:
                                MaxLength = CountMaxSentenceLength(MaxLength, fp, textFile)
                print('MaxLength for', character[:-1], 'case is: ', MaxLength)
                print('Number of sentence above threshold is: ', LongSentenceNumber)
                print('Average of sentence is: ', (TotalLength / NumberOfLine))
                if args.discourse:
                        writeBlackList(args.file_path.replace('\\','/'))
                else:
                        checkListOnly(args.file_path.replace('\\','/'))
                # print(entryList)

if __name__=="__main__":
        args = process_commands()
        processTextData(args)        