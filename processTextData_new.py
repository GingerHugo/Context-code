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
from sklearn.datasets import dump_svmlight_file

def process_commands():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('file_path')
        # parser.add_argument('voc_path')
        parser.add_argument('-model', action='store', default='BOW')
        parser.add_argument('-output', action='store_true', default=False)
        parser.add_argument('-discourse', action='store_true', default=False)
        return parser.parse_args()

Marker_set = set()
# StopWord_set = set()
LongSentenceNumber = 0
NumberOfLine = 0
TotalLength = 0
entryList = defaultdict(lambda: defaultdict(list))
SentenceThreshold = 60
polarSet = ['positive', 'negative']
MAXIMUN_LINE = 10000

def GetLabel(polar):
        if polar == 'positive':
                return 1
        else:
                return 0

def outputVectorSumExtractedFeaturesEntry(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddressDelete, posfix, Vector_word, dimension = 400, flag = False):
        # global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
        global  Marker_set, polarSet, MAXIMUN_LINE
        # LabelVector = []
        BlackListAddress = './Entry_processed/DeleteList'
        print("output {} file...".format(OutputAddress))
        with open(OutputAddress, 'w', encoding = 'utf-8') as fp2:
                with open(OutputAddressDelete, 'w', encoding = 'utf-8') as fp3:
                        for polar in polarSet:
                                label = GetLabel(polar)
                                with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
                                        BlackListName = '{}/Entry_{}_{}.txt'.format(BlackListAddress, polar, posfix)
                                        BlackList = set()
                                        ReadInBlackList(BlackList, BlackListName)
                                        FeatureVector = []
                                        FeatureVectorDelete = []
                                        LineCount = 0
                                        CurrentLine = 0
                                        for lines in fp:
                                                BlackFlag = 0
                                                LineCount += 1
                                                tempString = []
                                                tempStringDelete = []
                                                tempString.append(str(label))
                                                if CurrentLine not in BlackList:
                                                        BlackFlag = 1
                                                        tempStringDelete.append(str(label))
                                                # LabelVector.append(label)
                                                lineVector = np.zeros(dimension, dtype = 'float')
                                                # lineVectorDelete = np.zeros(dimension, dtype = 'float')
                                                line = lines[:-1]
                                                sentence = GetSentence(line, flag)
                                                for word in sentence.split():
                                                        candidate = GetCandiate(word, flag)
                                                        if  (candidate not in Marker_set):
                                                        # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                                lineVector = lineVector + Vector_word[candidate]
                                                                        # lineVectorDelete = lineVectorDelete + Vector_word[candidate]
                                                CurrentLine += 1
                                                tempString.append(' ' + ' '.join("{}:{}".format(i + 1, lineVector[i]) for i in range(0, dimension)))
                                                tempString.append('\n')
                                                if BlackFlag:
                                                        tempStringDelete.append(' ' + ' '.join("{}:{}".format(i + 1, lineVector[i]) for i in range(0, dimension)))
                                                        tempStringDelete.append('\n')
                                                if LineCount >= MAXIMUN_LINE:
                                                        fp2.write(''.join(FeatureVector))
                                                        if FeatureVectorDelete:
                                                                fp3.write(''.join(FeatureVectorDelete))
                                                        FeatureVector = []
                                                        FeatureVector.append(''.join(tempString))
                                                        FeatureVectorDelete = []
                                                        if BlackFlag:
                                                                FeatureVectorDelete.append(''.join(tempStringDelete))
                                                        LineCount = 0
                                                else:
                                                        FeatureVector.append(''.join(tempString))
                                                        if BlackFlag:
                                                                FeatureVectorDelete.append(''.join(tempStringDelete))
                                        fp2.write(''.join(FeatureVector))
                                        if FeatureVectorDelete:
                                                fp3.write(''.join(FeatureVectorDelete))

def outputVectorSumExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, dimension = 400, flag = True):
        # global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
        global  Marker_set, polarSet, MAXIMUN_LINE
        # LabelVector = []
        print("output {} file...".format(OutputAddress))
        with open(OutputAddress, 'w', encoding = 'utf-8') as fp2:
                for polar in polarSet:
                        label = GetLabel(polar)
                        with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
                                FeatureVector = []
                                LineCount = 0
                                for lines in fp:
                                        LineCount += 1
                                        tempString = []
                                        tempString.append(str(label))
                                        # LabelVector.append(label)
                                        lineVector = np.zeros(dimension, dtype = 'float')
                                        line = lines[:-1]
                                        sentence = GetSentence(line, flag)
                                        for word in sentence.split():
                                                candidate = GetCandiate(word, flag)
                                                # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                if  (candidate not in Marker_set):
                                                        lineVector = lineVector + Vector_word[candidate]
                                        tempString.append(' ' + ' '.join("{}:{}".format(i + 1, lineVector[i]) for i in range(0, dimension)))
                                        tempString.append('\n')
                                        if LineCount >= MAXIMUN_LINE:
                                                fp2.write(''.join(FeatureVector))
                                                FeatureVector = []
                                                FeatureVector.append(''.join(tempString))
                                                LineCount = 0
                                        else:
                                                FeatureVector.append(''.join(tempString))
                                fp2.write(''.join(FeatureVector))
                # X = np.array(FeatureVector, dtype = 'float')
                # Y = np.array(LabelVector, dtype = 'int')
                # dump_svmlight_file(X, Y, OutputAddress)

def outputTFIDFExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, flag = True):
        # global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
        global  Marker_set, polarSet, MAXIMUN_LINE
        print("output {} file...".format(OutputAddress))
        with open(OutputAddress, 'w', encoding = 'utf-8') as fp2:
                with open(OutputAddress2, 'w', encoding = 'utf-8') as fp3:
                        with open(OutputAddress3, 'w', encoding = 'utf-8') as fp4:
                                for polar in polarSet:
                                        label = GetLabel(polar)
                                        with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
                                                FeatureVector = []
                                                FeatureVectorTF = []
                                                FeatureVectorBinary = []
                                                LineCount = 0
                                                for lines in fp:
                                                        LineCount += 1
                                                        tempString = []
                                                        tempString.append(str(label))
                                                        tempStringTF = []
                                                        tempStringTF.append(str(label))
                                                        tempStringBinary = []
                                                        tempStringBinary.append(str(label))
                                                        line = lines[:-1]
                                                        sentence = GetSentence(line, flag)
                                                        TF = Counter()
                                                        for word in sentence.split():
                                                                candidate = GetCandiate(word, flag)
                                                                # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                                if  (candidate not in Marker_set):
                                                                        TF[candidate] += 1
                                                        value = defaultdict(float)
                                                        TFvalue = defaultdict(int)
                                                        for word in TF:
                                                                if IDFDict[word] == 0:
                                                                        print("IDF Zero Case", word)
                                                                        continue
                                                                value[Vocabulary[word]] = round(float(TF[word]) * math.log(float(N) / float(IDFDict[word])), 10)
                                                                TFvalue[Vocabulary[word]] = TF[word]
                                                        vector = OrderedDict(sorted(value.items(), key=lambda t: t[0]))
                                                        vectorTF = OrderedDict(sorted(TFvalue.items(), key=lambda t: t[0]))
                                                        tempString.append(' ' + ' '.join("{}:{}".format(i, vector[i]) for i in vector))
                                                        tempString.append('\n')
                                                        tempStringTF.append(' ' + ' '.join("{}:{}".format(i, vectorTF[i]) for i in vector))
                                                        tempStringTF.append('\n')
                                                        tempStringBinary.append(' ' + ' '.join("{}:{}".format(i, 1) for i in vector))
                                                        tempStringBinary.append('\n')
                                                        if LineCount >= MAXIMUN_LINE:
                                                                fp2.write(''.join(FeatureVector))
                                                                fp3.write(''.join(FeatureVectorTF))
                                                                fp4.write(''.join(FeatureVectorBinary))
                                                                FeatureVector = []
                                                                FeatureVectorTF = []
                                                                FeatureVectorBinary = []
                                                                FeatureVector.append(''.join(tempString))
                                                                FeatureVectorTF.append(''.join(tempStringTF))
                                                                FeatureVectorBinary.append(''.join(tempStringBinary))
                                                                LineCount = 0
                                                        else:
                                                                FeatureVector.append(''.join(tempString))
                                                                FeatureVectorTF.append(''.join(tempStringTF))
                                                                FeatureVectorBinary.append(''.join(tempStringBinary))
                                                fp2.write(''.join(FeatureVector))
                                                fp3.write(''.join(FeatureVectorTF))
                                                fp4.write(''.join(FeatureVectorBinary))

def outputTFIDFExtractedFeaturesNew(InputAddressPart1List, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, flag = True):
        # global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
        global  Marker_set, polarSet, MAXIMUN_LINE
        print("output {} file...".format(OutputAddress))
        with open(OutputAddress, 'w', encoding = 'utf-8') as fp2:
                with open(OutputAddress2, 'w', encoding = 'utf-8') as fp3:
                        with open(OutputAddress3, 'w', encoding = 'utf-8') as fp4:
                                for polar in polarSet:
                                        label = GetLabel(polar)
                                        for InputAddressPart1 in InputAddressPart1List:
                                                with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
                                                        FeatureVector = []
                                                        FeatureVectorTF = []
                                                        FeatureVectorBinary = []
                                                        LineCount = 0
                                                        for lines in fp:
                                                                LineCount += 1
                                                                tempString = []
                                                                tempString.append(str(label))
                                                                tempStringTF = []
                                                                tempStringTF.append(str(label))
                                                                tempStringBinary = []
                                                                tempStringBinary.append(str(label))
                                                                line = lines[:-1]
                                                                sentence = GetSentence(line, flag)
                                                                TF = Counter()
                                                                for word in sentence.split():
                                                                        candidate = GetCandiate(word, flag)
                                                                        # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                                                        if  (candidate not in Marker_set):
                                                                                TF[candidate] += 1
                                                                value = defaultdict(float)
                                                                TFvalue = defaultdict(int)
                                                                for word in TF:
                                                                        if IDFDict[word] == 0:
                                                                                print("IDF Zero Case", word)
                                                                                continue
                                                                        value[Vocabulary[word]] = round(float(TF[word]) * math.log(float(N) / float(IDFDict[word])), 10)
                                                                        TFvalue[Vocabulary[word]] = TF[word]
                                                                vector = OrderedDict(sorted(value.items(), key=lambda t: t[0]))
                                                                vectorTF = OrderedDict(sorted(TFvalue.items(), key=lambda t: t[0]))
                                                                tempString.append(' ' + ' '.join("{}:{}".format(i, vector[i]) for i in vector))
                                                                tempString.append('\n')
                                                                tempStringTF.append(' ' + ' '.join("{}:{}".format(i, vectorTF[i]) for i in vector))
                                                                tempStringTF.append('\n')
                                                                tempStringBinary.append(' ' + ' '.join("{}:{}".format(i, 1) for i in vector))
                                                                tempStringBinary.append('\n')
                                                                if LineCount >= MAXIMUN_LINE:
                                                                        fp2.write(''.join(FeatureVector))
                                                                        fp3.write(''.join(FeatureVectorTF))
                                                                        fp4.write(''.join(FeatureVectorBinary))
                                                                        FeatureVector = []
                                                                        FeatureVectorTF = []
                                                                        FeatureVectorBinary = []
                                                                        FeatureVector.append(''.join(tempString))
                                                                        FeatureVectorTF.append(''.join(tempStringTF))
                                                                        FeatureVectorBinary.append(''.join(tempStringBinary))
                                                                        LineCount = 0
                                                                else:
                                                                        FeatureVector.append(''.join(tempString))
                                                                        FeatureVectorTF.append(''.join(tempStringTF))
                                                                        FeatureVectorBinary.append(''.join(tempStringBinary))
                                                        fp2.write(''.join(FeatureVector))
                                                        fp3.write(''.join(FeatureVectorTF))
                                                        fp4.write(''.join(FeatureVectorBinary))

def GetTotalN(InputAddress, IDFDict, flag = True):
        # global Marker_set, StopWord_set
        global Marker_set
        count = 0
        with open(InputAddress, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        count += 1
                        line = lines[:-1]
                        sentence = GetSentence(line, flag)
                        wordBags = set()
                        for word in sentence.split():
                                candidate = GetCandiate(word, flag)
                                # if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                if  (candidate not in Marker_set):
                                        wordBags.add(candidate)
                        for word in wordBags:
                                IDFDict[word] += 1
        return count

def featureExtraction(args):
        # global Marker_set, StopWord_set, polarSet
        global Marker_set, polarSet
        StopWord_set = set()
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        IDFDict = Counter()
        Vocabulary = {}
        fileAddress = {('/rule-based/', 'naive_'), ('/discourse/', 'discourse_')}
        TypeSet = {'_automatic_'}
        CrossType = {'training'}
        prefixList = ['Context_', 'Comment_']
        preposfix = args.model + '_Feature_'
        postfix = '.txt'
        address2 = './Entry_processed/Comment_Extracted'
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress, prefixList)
        for tuples in combinations:
                if tuples[4].startswith('Context'):
                        GetWordCollection(Lexicon_Corpus, IDFDict,args.file_path.replace('\\','/') + tuples[3][0] + tuples[4] + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
                else:
                        GetWordCollection(Lexicon_Corpus, IDFDict, address2 + tuples[3][0] + tuples[4] + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
        for polar in polarSet:
                EntryfileName = args.file_path.replace('\\','/') + '/discourse/Context_discourse_{}_automatic_testing.txt'.format(polar)
                GetWordCollection(Lexicon_Corpus, IDFDict, EntryfileName, Marker_set, StopWord_set)
        CalculateVocabularySequence(Vocabulary, IDFDict)
        
        # Context feature for four methods with training and testing(TF-IDF)
        for lexiconType in TypeSet:
                for methodType in fileAddress:
                        combinations = itertools.product(polarSet, CrossType, prefixList)
                        N = 0
                        IDFDict = Counter()
                        for tuples in combinations:
                                if tuples[2].startswith("Context"):
                                        InputAddress = args.file_path.replace('\\','/') + methodType[0] + tuples[2] + methodType[1] + tuples[0] + lexiconType + tuples[1] + postfix
                                else:
                                        InputAddress = address2 + methodType[0] + tuples[2] + methodType[1] + tuples[0] + lexiconType + tuples[1] + postfix
                                N += GetTotalN(InputAddress, IDFDict, True)
                        fileBags = set()
                        for tuples in CrossType:
                                InputAddressPart1 = []
                                InputAddressPart1.append(args.file_path.replace('\\','/') + methodType[0] + prefixList[0] + methodType[1])
                                InputAddressPart1.append(address2 + methodType[0] + prefixList[1] + methodType[1])
                                InputAddressPart2 = lexiconType + tuples + postfix
                                OutputAddress = '{}/TF-IDF_feature/New_Clause_training_{}feature.txt'.format(args.file_path.replace('\\','/')[:-18], methodType[1])
                                OutputAddress2 = '{}/TF_feature/New_Clause_training_{}feature.txt'.format(args.file_path.replace('\\','/')[:-18], methodType[1])
                                OutputAddress3 = '{}/Boolean_feature/New_Clause_training_{}feature.txt'.format(args.file_path.replace('\\','/')[:-18], methodType[1])
                                outputTFIDFExtractedFeaturesNew(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, True)
        
        # Feature for training entry (context only entry training)
        N = 0
        IDFDict = Counter()
        for polar in polarSet:
                InputAddress = args.file_path.replace('\\','/') + '/discourse/Context_discourse_{}_automatic_testing.txt'.format(polar)
                N += GetTotalN(InputAddress, IDFDict, True)
        InputAddressPart1 = args.file_path.replace('\\','/') + '/discourse/Context_discourse_'
        InputAddressPart2 = '_automatic_testing.txt'
        OutputAddress = '{}/TF-IDF_feature/New_Clause_testing.txt'.format(args.file_path.replace('\\','/')[:-18])
        OutputAddress2 = '{}/TF_feature/New_Clause_testing.txt'.format(args.file_path.replace('\\','/')[:-18])
        OutputAddress3 = '{}/Boolean_feature/New_Clause_testing.txt'.format(args.file_path.replace('\\','/')[:-18])
        outputTFIDFExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, True)

def processTextData(args):
        global LongSentenceNumber, NumberOfLine, TotalLength
        path = './Entry_processed/connectives.csv'
        ReadInReverseDiscourseMarker(Marker_set, path)
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
                for textFile in fileList:
                        print(textFile)
                        if textFile.startswith('/rule-based/Context') or textFile.startswith('/discourse/Context'):
                                with open(args.file_path.replace('\\','/') + textFile, 'r', encoding = 'utf-8') as fp:
                                        tuples = CountMaxSentenceLength(MaxLength, fp, textFile)
                        else:
                                Address2 = './Entry_processed/Comment_Extracted/'
                                with open(Address2 + textFile, 'r', encoding = 'utf-8') as fp:
                                        tuples = CountMaxSentenceLength(MaxLength, fp, textFile)
                LongSentenceNumber = tuples[2]
                MaxLength = tuples[0]
                NumberOfLine = tuples[1]
                TotalLength = tuples[3]
                print('MaxLength for', character[:-1], 'case is: ', MaxLength)
                print('Number of sentence above threshold is: ', LongSentenceNumber)
                print('Average of sentence is: ', (TotalLength / NumberOfLine))

if __name__=="__main__":
        args = process_commands()
        processTextData(args)        