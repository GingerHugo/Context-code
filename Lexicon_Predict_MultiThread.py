import DiscourseMarker
from collections import *
from math import *
import sys
import threading
from commonDiscourseMarker import *
from commonIO import *
import itertools
from random import randint

total_correct = 0
total_count = 0
threadLock = threading.Lock()

def GetLabel(polar):
        if polar == 'positive':
                return 1
        else:
                return 0

def ReadInPasringResult(DP_file, DP_Result, polar):
        Label = GetLabel(polar)
        count = 0
        with open(DP_file, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        DP_Result[Label][count] = line
                        count += 1

class myThread (threading.Thread):
        def __init__(self, threadID, name, Max_iterTime, VocabularyAddress, POSAddress, NegatorAddress, ParseResultAddress, BlackListAddress, element):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.Max_iterTime = Max_iterTime
                self.VocabularyAddress = VocabularyAddress
                self.POSAddress = POSAddress
                self.NegatorAddress = NegatorAddress
                self.ParseResultAddress = ParseResultAddress
                self.BlackListAddress = BlackListAddress
                self.element = element
        def run(self):          # Codes to be executed by multi-thread
                global total_correct
                global total_count
                LexiconPositive = set()
                LexiconNegative = set()
                negator_set = set()
                polarizationSet = ['positive', 'negative']
                for polar in polarizationSet:
                        fileName = '{}/{}/voc_{}_final_{}{}.txt'.format(self.VocabularyAddress, self.element[1][0], self.element[1][1], polar, self.element[0][1])
                        if  polar == 'positive':
                                ReadInLexicon(LexiconPositive, fileName)
                        else:
                                ReadInLexicon(LexiconNegative, fileName)
                intersection = LexiconNegative & LexiconPositive
                if intersection:
                        print("Lexicon not mutually exclusive!!!")
                        print(intersection)
                ReadInNegator(negator_set, self.NegatorAddress)
                DP_Result = defaultdict(dict)
                for polar in polarizationSet:
                        DP_file = '{}/DPResult_Segmented_Entry_{}_testing.txt'.format(self.ParseResultAddress, polar)
                        ReadInPasringResult(DP_file, DP_Result, polar)
                for x in range(0, self.Max_iterTime):                        
                        for polar in polarizationSet:
                                fileName = '{}/POSTagged_Entry_{}_testing.txt'.format(self.POSAddress, polar)
                                BlackListName = '{}/Entry_{}_testing.txt'.format(self.BlackListAddress, polar)
                                BlackList = set()
                                ReadInBlackList(BlackList, BlackListName)
                                # print(fileName)
                                # print(BlackListName)
                                (correct, total) = ProcessingCommentFile(fileName, BlackList, polar, DP_Result, LexiconPositive, LexiconNegative, negator_set)
                                threadLock.acquire()
                                total_count += total
                                total_correct += correct
                                # print(total)
                                # print(correct)
                                threadLock.release()

def ProcessingCommentFile(fileName, BlackList, polar, DP_Result, LexiconPositive, LexiconNegative, negator_set):
        FileLabel = GetLabel(polar)
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                countLine = 0
                countNum = 0
                total_correct = 0
                for lines in fp:
                        line = lines[:-1]
                        if countLine in BlackList:
                                countLine += 1
                                continue
                        countNum += 1
                        Bags = line.split()
                        DP_Result_line = DP_Result[FileLabel][countLine]
                        DPResultDict = defaultdict(dict)
                        ParseTheDPResult(DPResultDict, DP_Result_line)
                        x = 0
                        voting = 0 
                        for words in Bags:
                                words = '{}-{}'.format(words.rsplit('#', 1)[0], words.rsplit('#', 1)[1])
                                if (words not in LexiconPositive) and (words not in LexiconNegative):
                                        x += 1
                                        continue
                                else:
                                        if words in LexiconPositive:
                                                result = 1
                                        else:
                                                result = 0
                                        word = words.rsplit('#', 1)[0]
                                        Negatorflag = CheckNegatorFromDP(word, x, DPResultDict, negator_set)
                                        x += 1
                                        if ((Negatorflag)^result):
                                                voting += 1
                                        else:
                                                voting -= 1
                        if voting > 0:
                                FlagTemp = 1
                        elif voting < 0:
                                FlagTemp = 0
                        else:
                                FlagTemp = randint(0,1)
                        countLine += 1
                        if FlagTemp == FileLabel:
                                total_correct += 1
        return (total_correct, countNum)

def predictEntry(VocabularyAddress, POSAddress, NegatorAddress, ParseResultAddress, BlackListAddress, element):
        global total_correct
        global total_count
        thread_num = 20
        Max_iterTime = 50
        threads = []
        total_correct = 0
        total_count = 0
        for x in range(0, thread_num):
                name = 'Thread-{}'.format(x + 1)
                thread = myThread(x + 1, name, Max_iterTime, VocabularyAddress, POSAddress, NegatorAddress, ParseResultAddress, BlackListAddress, element)
                thread.start()
                threads.append(thread)

        # 等待所有线程完成
        for t in threads:
                t.join()
        print ("Exiting Main Thread")
        average_correct = total_correct / (thread_num * Max_iterTime)
        average_total = total_count / (thread_num * Max_iterTime)
        average_correct = int(round(average_correct, 0))
        average_total = int(round(average_total, 0))
        average_accuracy = round(float(total_correct) / float(total_count), 4)
        print("average_correct for {} {} case is: {}".format(element[0][0], element[1][1], average_correct))
        print("average_total for {} {} case is: {}".format(element[0][0], element[1][1], average_total))
        print("average_accuracy for {} {} case is: {}".format(element[0][0], element[1][1], average_accuracy))

def BuildingDiscourse_Multi(argv): 
        sys.setrecursionlimit(2000) 
        NegatorAddress = './Entry_processed/negator.txt'
        ParseResultAddress = './Entry_processed/DP_Result'
        VocabularyAddress = './Entry_processed/lexicon_build'
        BlackListAddress = './Entry_processed/DeleteList'
        POSAddress = './Entry_processed/POSTagged'
        polarizationSet = ['positive', 'negative']
        lexicon_set = {('automatic', ''), ('manual_corrected', '_man_corrected')}
        fileAddress = {('rule-based', 'naive'), ('discourse', 'discourse')}
        combinations = itertools.product(lexicon_set, fileAddress)
        for element in combinations:              
                predictEntry(VocabularyAddress, POSAddress, NegatorAddress, ParseResultAddress, BlackListAddress, element)


if __name__ == '__main__':
        BuildingDiscourse_Multi(sys.argv[1:])