from collections import defaultdict
import numpy as np
import sys, re
# import pandas as pd
from commonDiscourseMarker import *
from commonIO import *
import itertools
from transform2vecDNN import *
from processTextData import *

def CountMaxSentenceLength(MaxLength, fp, textFile):
        global Marker_set, StopWord_set, LongSentenceNumber
        global NumberOfLine, TotalLength, entryList, SentenceThreshold
        for lines in fp:
                NumberOfLine += 1
                line = lines[:-1]
                entryType = line.split('@@@@', 1)[0]
                entryNumber = line.split('@@@@', 2)[1]
                sentence = line.split(' ', 1)[1]
                count = 0
                for word in sentence.split():
                        candidate = word.rsplit('#', 1)[0]
                        if  (candidate not in Marker_set) and (candidate not in StopWord_set):
                                count += 1
                TotalLength += count
                if count > MaxLength:
                        MaxLength = count
                if count > SentenceThreshold:
                        # print (sentence)
                        if textFile[-11: -4] == 'testing':
                                LongSentenceNumber += 1
                                if entryList.get(entryType, 0):
                                        entryList[entryType]['testing'].append(entryNumber)
                                else:
                                        temp = defaultdict(list)
                                        temp['testing'].append(entryNumber)
                                        entryList[entryType] = temp
                        else:
                                if entryList.get(entryType, 0):
                                        # print('here')
                                        entryList[entryType]['training'].append(entryNumber)
                                else:
                                        temp = defaultdict(list)
                                        temp['training'].append(entryNumber)
                                        # print('here')
                                        entryList[entryType] = temp
        return MaxLength

def TraverseFileName(fileName, character):
        polarSet = {'positive', 'negative'}
        TypeSet = {'_automatic_', '_manual_corrected_'}
        CrossType = {'training', 'testing'}
        prefix = 'Context_'
        postfix = '.txt'
        combinations = itertools.product(polarSet, TypeSet, CrossType)
        for tuples in combinations:
                yield (fileName + prefix + character + tuples[0] + tuples[1] + tuples[2] + postfix)

def writeBlackList(Address):
        global entryList 
        for entryType in entryList:
                # print(entryList[entryType])
                for experimentType in entryList[entryType]:
                        result = entryList[entryType][experimentType]
                        if entryType == 'P':
                                prefix = 'positive_'
                        else:
                                prefix = 'negative_'
                        postfix = '.txt'
                        # with open(Address[:-18] + '/DeleteList/' + prefix + experimentType + postfix, 'a', encoding = 'utf-8') as fp:
                        #         for element in result:
                        #                 fp.write(element + '\n')
                        print(prefix[:-1], ' ', experimentType, ' number of delete list are')
                        print(len(result))

def checkListOnly(Address):
        global entryList 
        for entryType in entryList:
                # print(entryList[entryType])
                for experimentType in entryList[entryType]:
                        result = entryList[entryType][experimentType]
                        if entryType == 'P':
                                prefix = 'positive_'
                        else:
                                prefix = 'negative_'
                        postfix = '.txt'
                        # with open(Address[:-18] + '/DeleteList/' + prefix + experimentType + postfix, 'a', encoding = 'utf-8') as fp:
                        #         for element in result:
                        #                 fp.write(element + '\n')
                        print(prefix[:-1], ' ', experimentType, ' number of delete list are')
                        print(len(result))
