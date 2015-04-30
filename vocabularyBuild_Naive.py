import string  
import re  
import sys
import os
from collections import *
from math import *
from commonDiscourseMarker import *
from commonIO import *

SignSet = {'，#PU', ',#PU', '。#PU', '.#PU', '！#PU', '!#PU', '?#PU', '？#PU', '；#PU', ';#PU'}

def GetTotalNumber(fileAddress):
        global SignSet
        count = 0
        with open(fileAddress, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        line = ' ' + line
                        clauses = re.split(r' [，|,|。|\.|！|\!|\?|？|；|;]#PU', line)
                        # re.split(r' ，#PU| ,#PU| 。#PU| \.#PU| ！#PU| \!#PU| \?#PU| ？#PU| ；#PU| ;#PU', line)
                        for each in clauses:
                                if each and each.strip() and each.strip().rstrip():
                                        count += 1
        return count

def BuildingTheVocab(flag, DPparser_file, POStagged_file, negator_set, ClauseTotalNumber):
        global POSset
        global EntryCount
        global WordCount

        stopList = {'－－－－－','－'}
        with open(DPparser_file, 'r', encoding = 'utf-8') as fp:
                with open(POStagged_file, 'r', encoding = 'utf-8') as fp2:
                        for lines in fp:
                                DPResult = defaultdict(dict)
                                line = lines[:-1]
                                POSline = fp2.readline()[:-1]
                                ParseTheDPResult(DPResult, line)
                                it = 0
                                POSline = ' ' + POSline
                                clauses = re.split(r' [，|,|。|\.|！|\!|\?|？|；|;]#PU', POSline)
                                # clauses = re.split('\，#PU|\,#PU|\。#PU|\.#PU|\！#PU|\!#PU|\?#PU|\？#PU|\；#PU|\;#PU', POSline)
                                for each in clauses:
                                        if each and each.strip() and each.strip().rstrip():
                                                temp = each.strip().rstrip()
                                                words = temp.split()
                                                for x in range(0, len(words)):
                                                        # print(words[x])
                                                        try:
                                                                word = words[x].rsplit('#', 1)[0]
                                                                POS_tag = words[x].rsplit('#', 1)[1]
                                                        except:
                                                                print(words[x])
                                                        else:
                                                                pass                                                       
                                                        # print(word)
                                                        # print(POS_tag)
                                                        if POS_tag not in POSset:
                                                                continue
                                                        elif word in stopList:
                                                                continue
                                                        else:
                                                                Negatorflag = CheckNegatorFromDP(word, (it + x), DPResult, negator_set)
                                                                final = (Negatorflag^flag)
                                                                if final:
                                                                        WordCount[word]['positive'] += 1
                                                                        if EntryCount.get(word, 0):
                                                                                if final != flag:
                                                                                        EntryCount[word]['positive'] += 1
                                                                                        EntryCount[word]['negative'] -= 1
                                                                        else:
                                                                                EntryCount[word]['positive'] = ClauseTotalNumber['positive']
                                                                                EntryCount[word]['negative'] = ClauseTotalNumber['negative']
                                                                                if final != flag:
                                                                                        EntryCount[word]['positive'] += 1
                                                                                        EntryCount[word]['negative'] -= 1
                                                                else:
                                                                        # EntryCount['negative'] += 1
                                                                        WordCount[word]['negative'] += 1
                                                                        if EntryCount.get(word, 0):
                                                                                if final != flag:
                                                                                        EntryCount[word]['positive'] -= 1
                                                                                        EntryCount[word]['negative'] += 1
                                                                        else:
                                                                                EntryCount[word]['positive'] = ClauseTotalNumber['positive']
                                                                                EntryCount[word]['negative'] = ClauseTotalNumber['negative']
                                                                                if final != flag:
                                                                                        EntryCount[word]['positive'] -= 1
                                                                                        EntryCount[word]['negative'] += 1
                                                it += len(words)
                                        it += 1

POSset = set()
EntryCount = defaultdict(Counter)
WordCount = defaultdict(Counter)

def BuildingMain(argv):
        global POSset
        global EntryCount
        global WordCount
        None_set = {"NR", "NT", "NN"}
        Verb_set = {"VA", "VC", "VE", "VV"}
        Advb_set = {"AD"}
        Adjc_set = {"JJ"}
        threshold = 10           # At least appears ten times
        POSset = Verb_set | Advb_set | Adjc_set
        threshold = 10
        ClauseTotalNumber = {}
        polarization = {'positive','negative'}
        ParseResultAddress = './Entry_processed/DP_Result/'
        POSaddress = './Entry_processed/POSTagged/'
        DPprefix = 'DPResult_Segmented_Entry_'
        POSprefix = 'POSTagged_Entry_'
        postfix = '_training.txt'
        path = './negator.txt'
        negator_set = set()
        ReadInNegator(negator_set, path)
        for polar in polarization:
                pos_file_address = POSaddress + POSprefix + polar + postfix
                ClauseTotalNumber[polar] = GetTotalNumber(pos_file_address)
        # mutex = multiprocessing.RLock()       # mutex lock of multi-threading
        for polar in polarization:
                if polar == 'positive':
                        flag = 1
                else:
                        flag = 0
                DPparser_file = ParseResultAddress + DPprefix + polar + postfix
                POStagged_file = POSaddress + POSprefix + polar + postfix
                BuildingTheVocab(flag, DPparser_file, POStagged_file, negator_set, ClauseTotalNumber)
        package = []
        Calculation(package, threshold, EntryCount, WordCount, ClauseTotalNumber)
        OutputResult(package, 'naive')

if __name__ == '__main__':
        BuildingMain(sys.argv[1:])