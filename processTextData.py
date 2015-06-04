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
polarSet = ['positive', 'negative']
MAXIMUN_LINE = 10000

def GetLabel(polar):
        if polar == 'positive':
                return 1
        else:
                return 0

# def outputCNNExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, MaxLength = 60, ConvolLengh = 6, dimension = 400, flag = True):
#         global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
#         # LabelVector = ''
#         print("output {} file...".format(OutputAddress))
#         with open(OutputAddress, 'w', encoding = 'utf-8') as fp2:
#                 for polar in polarSet:
#                         label = GetLabel(polar)
#                         with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
#                                 LineCount = 0
#                                 FeatureVector = []
#                                 for lines in fp:
#                                         LineCount += 1
#                                         tempString = []
#                                         tempString.append(str(label))
#                                         # LabelVector.append(label)
#                                         # lineVector = np.zeros(((MaxLength + (2 * (ConvolLengh - 1))) * dimension), dtype = 'float')
#                                         Initial = ConvolLengh
#                                         line = lines[:-1]
#                                         sentence = GetSentence(line, flag)
#                                         for word in sentence.split():
#                                                 candidate = GetCandiate(word, flag)
#                                                 if  (candidate not in Marker_set) and (candidate not in StopWord_set):
#                                                         begin  =((Initial - 1) * dimension + 1)
#                                                         wordVec = Vector_word[candidate]
#                                                         tempString.append(' ' + ' '.join("{}:{}".format(i, wordVec[i - begin]) for i in range(begin, begin + dimension)))
#                                                         Initial += 1
#                                         tempString.append('\n')
#                                         if LineCount >= MAXIMUN_LINE:
#                                                 fp2.write(''.join(FeatureVector))
#                                                 FeatureVector = []
#                                                 FeatureVector.append(''.join(tempString))
#                                                 LineCount = 0
#                                         else:
#                                                 FeatureVector.append(''.join(tempString))
#                                 fp2.write(''.join(FeatureVector))
#                 #                         FeatureVector.append(lineVector)
#                 # X = np.array(FeatureVector, dtype = 'float')
#                 # Y = np.array(LabelVector, dtype = 'int')
#                 # dump_svmlight_file(X, Y, OutputAddress)

def outputVectorSumExtractedFeaturesEntry(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddressDelete, posfix, Vector_word, dimension = 400, flag = False):
        global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
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
                                                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
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
        global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
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
                                                if  (candidate not in Marker_set) and (candidate not in StopWord_set):
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
        global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
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
                                                                if  (candidate not in Marker_set) and (candidate not in StopWord_set):
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

def outputTFIDFExtractedFeaturesEntry(InputAddressPart1, InputAddressPart2, OutputList, posfix, IDFDict, N, Vocabulary, flag = False):
        global  Marker_set, StopWord_set, polarSet, MAXIMUN_LINE
        BlackListAddress = './Entry_processed/DeleteList'
        print("output {} file...".format(OutputList))
        with open(OutputList[0], 'w', encoding = 'utf-8') as fp2:
                with open(OutputList[2], 'w', encoding = 'utf-8') as fp3:
                        with open(OutputList[4], 'w', encoding = 'utf-8') as fp4:
                                with open(OutputList[1], 'w', encoding = 'utf-8') as fp5:
                                        with open(OutputList[3], 'w', encoding = 'utf-8') as fp6:
                                                with open(OutputList[5], 'w', encoding = 'utf-8') as fp7:
                                                        for polar in polarSet:
                                                                label = GetLabel(polar)
                                                                with open(InputAddressPart1 + polar + InputAddressPart2, 'r', encoding = 'utf-8') as fp:
                                                                        BlackListName = '{}/Entry_{}_{}.txt'.format(BlackListAddress, polar, posfix)
                                                                        BlackList = set()
                                                                        ReadInBlackList(BlackList, BlackListName)
                                                                        FeatureVector = []
                                                                        FeatureVectorTF = []
                                                                        FeatureVectorBinary = []
                                                                        FeatureVectorDelete = []
                                                                        FeatureVectorTFDelete = []
                                                                        FeatureVectorBinaryDelete = []
                                                                        LineCount = 0
                                                                        CurrentLine = 0
                                                                        for lines in fp:
                                                                                BlackFlag = 0
                                                                                LineCount += 1
                                                                                tempString = []
                                                                                tempString.append(str(label))
                                                                                tempStringTF = []
                                                                                tempStringTF.append(str(label))
                                                                                tempStringBinary = []
                                                                                tempStringBinary.append(str(label))
                                                                                tempStringDelete = []
                                                                                tempStringTFDelete = []
                                                                                tempStringBinaryDelete = []
                                                                                if CurrentLine not in BlackList:
                                                                                        BlackFlag = 1
                                                                                        tempStringDelete.append(str(label))
                                                                                        tempStringTFDelete.append(str(label))
                                                                                        tempStringBinaryDelete.append(str(label))
                                                                                line = lines[:-1]
                                                                                CurrentLine += 1
                                                                                sentence = GetSentence(line, flag)
                                                                                TF = Counter()
                                                                                for word in sentence.split():
                                                                                        candidate = GetCandiate(word, flag)
                                                                                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
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
                                                                                if BlackFlag:
                                                                                        tempStringDelete.append(' ' + ' '.join("{}:{}".format(i, vector[i]) for i in vector))
                                                                                        tempStringDelete.append('\n')
                                                                                        tempStringTFDelete.append(' ' + ' '.join("{}:{}".format(i, vectorTF[i]) for i in vector))
                                                                                        tempStringTFDelete.append('\n')
                                                                                        tempStringBinaryDelete.append(' ' + ' '.join("{}:{}".format(i, 1) for i in vector))
                                                                                        tempStringBinaryDelete.append('\n')
                                                                                if LineCount >= MAXIMUN_LINE:
                                                                                        fp2.write(''.join(FeatureVector))
                                                                                        fp3.write(''.join(FeatureVectorTF))
                                                                                        fp4.write(''.join(FeatureVectorBinary))
                                                                                        if FeatureVectorDelete:
                                                                                                fp5.write(''.join(FeatureVectorDelete))
                                                                                                if not FeatureVectorTFDelete:
                                                                                                        print("error case!! Line 317")
                                                                                                fp6.write(''.join(FeatureVectorTFDelete))
                                                                                                if not FeatureVectorBinaryDelete:
                                                                                                        print("error case!! Line 321")
                                                                                                fp7.write(''.join(FeatureVectorBinaryDelete))
                                                                                        FeatureVector = []
                                                                                        FeatureVectorTF = []
                                                                                        FeatureVectorBinary = []
                                                                                        FeatureVectorDelete = []
                                                                                        FeatureVectorTFDelete = []
                                                                                        FeatureVectorBinaryDelete = []
                                                                                        FeatureVector.append(''.join(tempString))
                                                                                        FeatureVectorTF.append(''.join(tempStringTF))
                                                                                        FeatureVectorBinary.append(''.join(tempStringBinary))
                                                                                        if BlackFlag:
                                                                                                FeatureVectorDelete.append(''.join(tempStringDelete))
                                                                                                FeatureVectorTFDelete.append(''.join(tempStringTFDelete))
                                                                                                FeatureVectorBinaryDelete.append(''.join(tempStringBinaryDelete))
                                                                                        LineCount = 0
                                                                                else:
                                                                                        FeatureVector.append(''.join(tempString))
                                                                                        FeatureVectorTF.append(''.join(tempStringTF))
                                                                                        FeatureVectorBinary.append(''.join(tempStringBinary))
                                                                                        if BlackFlag:
                                                                                                FeatureVectorDelete.append(''.join(tempStringDelete))
                                                                                                FeatureVectorTFDelete.append(''.join(tempStringTFDelete))
                                                                                                FeatureVectorBinaryDelete.append(''.join(tempStringBinaryDelete))
                                                                        fp2.write(''.join(FeatureVector))
                                                                        fp3.write(''.join(FeatureVectorTF))
                                                                        fp4.write(''.join(FeatureVectorBinary))
                                                                        if FeatureVectorDelete:
                                                                                fp5.write(''.join(FeatureVectorDelete))
                                                                                if not FeatureVectorTFDelete:
                                                                                        print("error case!! Line 351")
                                                                                fp6.write(''.join(FeatureVectorTFDelete))
                                                                                if not FeatureVectorBinaryDelete:
                                                                                        print("error case!! Line 353")
                                                                                fp7.write(''.join(FeatureVectorBinaryDelete))

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
        global Marker_set, StopWord_set, polarSet
        Lexicon_Corpus = Counter()
        Vector_word = Counter()
        IDFDict = Counter()
        Vocabulary = {}
        fileAddress = {('/rule-based/', 'naive_'), ('/discourse/', 'discourse_')}
        TypeSet = {'_automatic_', '_manual_corrected_'}
        CrossType = {'training', 'testing'}
        prefix = 'Context_'
        preposfix = args.model + '_Feature_'
        postfix = '.txt'
        combinations = itertools.product(polarSet, TypeSet, CrossType, fileAddress)
        for tuples in combinations:
                GetWordCollection(Lexicon_Corpus, IDFDict,args.file_path.replace('\\','/') + tuples[3][0] + prefix + tuples[3][1] + tuples[0] + tuples[1] + tuples[2] + postfix, Marker_set, StopWord_set)
        EntryAddress = './Entry_processed/Entry_segmented'
        combinations = itertools.product(polarSet, CrossType)
        for tuples in combinations:
                EntryfileName = '{}/Segmented_Entry_{}_{}.txt'.format(EntryAddress, tuples[0], tuples[1])
                GetWordCollection(Lexicon_Corpus, IDFDict, EntryfileName, Marker_set, StopWord_set, False)
        CalculateVocabularySequence(Vocabulary, IDFDict)
        # OOVWord = ReadInVector(args.voc_path, Vector_word, Lexicon_Corpus, args.model)
        # AddOOVVectors(Vector_word, Lexicon_Corpus, OOVWord, min_df=1, k=400)
        # combinations = itertools.product(TypeSet, CrossType, fileAddress)
        # fileBags = set()

        # # Context feature for four methods with training and testing(CNN, vector summation)
        # for tuples in combinations:
        #         InputAddressPart1 = args.file_path.replace('\\','/') + tuples[2][0] + prefix + tuples[2][1]
        #         InputAddressPart2 = tuples[0] + tuples[1] + postfix
        #         # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/CNN_feature/' + tuples[2][0][1:] + preposfix + tuples[2][1] + tuples[0][1:] + tuples[1] + postfix
        #         # outputCNNExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 60, 6, 400, True)
        #         OutputAddress = args.file_path.replace('\\','/')[:-18] + '/wordVector_feature/' + tuples[2][0][1:] + preposfix + tuples[2][1] + tuples[0][1:] + tuples[1] + postfix
        #         outputVectorSumExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 400, True)
        
        # Whole entry with training and testing
        for tuples in CrossType:
                InputAddressPart1 = '{}/Segmented_Entry_'.format(EntryAddress)
                InputAddressPart2 = '_{}.txt'.format(tuples)
                # OutputAddress = "{}/wordVector_feature/Segmented_Entry_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                # OutputAddressDelete = "{}/wordVector_feature/Segmented_Entry_deleted_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                # outputVectorSumExtractedFeaturesEntry(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddressDelete, tuples, Vector_word, 400, False)
                N = 0
                IDFDict = Counter()
                for polar in polarSet:
                        InputAddress = InputAddressPart1 + polar + InputAddressPart2
                        N += GetTotalN(InputAddress, IDFDict, False)
                OutputAddress = "{}/TF-IDF_feature/Segmented_Entry_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                OutputAddressDelete = "{}/TF-IDF_feature/Segmented_Entry_deleted_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                OutputAddress2 = "{}/TF_feature/Segmented_Entry_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                OutputAddressDelete2 = "{}/TF_feature/Segmented_Entry_deleted_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                OutputAddress3 = "{}/Boolean_feature/Segmented_Entry_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                OutputAddressDelete3 = "{}/Boolean_feature/Segmented_Entry_deleted_{}.txt".format(args.file_path.replace('\\','/')[:-18], tuples)
                # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + preposfix + 'TestEntry' + postfix
                # OutputAddress2 = args.file_path.replace('\\','/')[:-18] + '/TF_feature/' + preposfix + 'TestEntry' + postfix
                # OutputAddress3 = args.file_path.replace('\\','/')[:-18] + '/Boolean_feature/' + preposfix + 'TestEntry' + postfix
                OutputList = [OutputAddress, OutputAddressDelete, OutputAddress2, OutputAddressDelete2, OutputAddress3, OutputAddressDelete3]
                outputTFIDFExtractedFeaturesEntry(InputAddressPart1, InputAddressPart2, OutputList, tuples, IDFDict, N, Vocabulary, False)
        
        # Context feature for four methods with training and testing(TF-IDF)
        textPrefix = 'Context_Entire_Doc_'
        textPosfix = '_testing.txt'
        trainTextPrefix = 'Context_Entire_Doc_'
        trainTextPosfix = '_training.txt'
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
                        for tuples in CrossType:
                                InputAddressPart1 = args.file_path.replace('\\','/') + methodType[0] + prefix + methodType[1]
                                InputAddressPart2 = lexiconType + tuples + postfix
                                OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + methodType[0][1:] + preposfix + methodType[1] + lexiconType[1:] + tuples + postfix
                                OutputAddress2 = args.file_path.replace('\\','/')[:-18] + '/TF_feature/' + methodType[0][1:] + preposfix + methodType[1] + lexiconType[1:] + tuples + postfix
                                OutputAddress3 = args.file_path.replace('\\','/')[:-18] + '/Boolean_feature/' + methodType[0][1:] + preposfix + methodType[1] + lexiconType[1:] + tuples + postfix
                                outputTFIDFExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, True)
        
        # Feature for training entry (context only entry training)
        N = 0
        IDFDict = Counter()
        for polar in polarSet:
                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_Extracted/' + trainTextPrefix + polar + trainTextPosfix
                N += GetTotalN(InputAddress, IDFDict, False)
        InputAddressPart1 = args.file_path.replace('\\','/')[:-18] + '/Context_Extracted/' + trainTextPrefix
        InputAddressPart2 = trainTextPosfix
        # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/CNN_feature/' + trainTextPrefix + 'TrainDocEntry' + postfix
        # outputCNNExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 60, 6, 400, False)
        # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/wordVector_feature/' + trainTextPrefix + 'TrainDocEntry' + postfix
        # outputVectorSumExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 400, False)
        OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + preposfix + 'TrainDocEntry' + postfix
        OutputAddress2 = args.file_path.replace('\\','/')[:-18] + '/TF_feature/' + preposfix + 'TrainDocEntry' + postfix
        OutputAddress3 = args.file_path.replace('\\','/')[:-18] + '/Boolean_feature/' + preposfix + 'TrainDocEntry' + postfix
        outputTFIDFExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, False)


        # Feature for test entry (context only entry testing)
        N = 0
        IDFDict = Counter()
        for polar in polarSet:
                InputAddress = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix + polar + textPosfix
                N += GetTotalN(InputAddress, IDFDict, False)
        InputAddressPart1 = args.file_path.replace('\\','/')[:-18] + '/Context_testing/' + textPrefix
        InputAddressPart2 = textPosfix
        # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/CNN_feature/' + preposfix + 'TestEntry' + postfix
        # outputCNNExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 60, 6, 400, False)
        # OutputAddress = args.file_path.replace('\\','/')[:-18] + '/wordVector_feature/' + preposfix + 'TestEntry' + postfix
        # outputVectorSumExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, Vector_word, 400, False)
        OutputAddress = args.file_path.replace('\\','/')[:-18] + '/TF-IDF_feature/' + preposfix + 'TestEntry' + postfix
        OutputAddress2 = args.file_path.replace('\\','/')[:-18] + '/TF_feature/' + preposfix + 'TestEntry' + postfix
        OutputAddress3 = args.file_path.replace('\\','/')[:-18] + '/Boolean_feature/' + preposfix + 'TestEntry' + postfix
        outputTFIDFExtractedFeatures(InputAddressPart1, InputAddressPart2, OutputAddress, OutputAddress2, OutputAddress3, IDFDict, N, Vocabulary, False)

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