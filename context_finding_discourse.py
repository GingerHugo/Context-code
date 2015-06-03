import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys
import threading
from commonIO import *
from commonDiscourseMarker import *
import sys

total = 0
positive_case = 0
negative_case = 0
lineCount = 0
threadLock = threading.Lock()

class myThread (threading.Thread):
        def __init__(self, threadID, name, counter, fp, fp1, fp2, fp3, fp4, flag, lexiconType, BlackList):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.counter = counter
                self.fp = fp
                self.Pfp = fp1
                self.Nfp = fp2
                self.Pcomfp = fp3
                self.Ncomfp = fp4
                self.flag = flag
                self.postfix = lexiconType
                self.BlackList = BlackList
        def run(self):          #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
                global total
                global positive_case
                global negative_case
                global lineCount
                Lexicon = set()
                # initial_set = set()
                polarization = {'positive','negative'}
                Address_lex = './Entry_processed/lexicon_build/discourse/'
                threadLock.acquire()
                # Get_initial('./experiment/Entry_processed/connectives.csv', initial_set)
                for polar in polarization:
                        if self.postfix == 'automatic_':
                                fileName = Address_lex + 'voc_discourse_final_' + polar + '.txt'
                        else:
                                fileName = Address_lex + 'voc_discourse_final_' + polar + '_man_corrected.txt'
                        ReadInLexicon(Lexicon, fileName)
                detector = DiscourseMarker.LinkageDetector('./Entry_processed/connectives.csv')
                line = self.fp.readline()
                CurrentLine = lineCount
                lineCount += 1
                while CurrentLine in self.BlackList:
                        line = self.fp.readline()
                        CurrentLine = lineCount
                        lineCount += 1
                threadLock.release()
                if self.flag:
                        lineInit = 'P'
                else:
                        lineInit = 'N'
                middleFix = '@@@@'        
                while line:
                        line = line[:-1]
                        if not line.startswith('(ROOT'):
                                threadLock.acquire()
                                line = self.fp.readline()
                                CurrentLine = lineCount
                                lineCount += 1
                                while CurrentLine in self.BlackList:
                                        line = self.fp.readline()
                                        CurrentLine = lineCount
                                        lineCount += 1
                                threadLock.release()
                                continue
                        try:
                                ptree = ParentedTree.fromstring(line)
                        except:
                                # print(count_line)
                                line = line.replace('(PU )','(PU ）')
                                line = line.replace('(PU (','(PU （')
                                ptree = ParentedTree.fromstring(line)
                        else:
                                pass
                        # ptree = ParentedTree.fromstring(line)
                        sentence = ptree.leaves()
                        sequence = ptree.pos()
                        Index = ptree.treepositions('leaves')
                        IP_range = {}
                        GetIPRange(ptree, IP_range)
                        DiscourseLabel = defaultdict(dict)
                        Marker_range_set = set()
                        PriorityDecision(detector.detect_by_tokens(sentence), \
                                IP_range, DiscourseLabel, ptree, Marker_range_set)
                        threadLock.acquire()
                        for clause_number in DiscourseLabel:
                                # positive_context = ''
                                # negative_context = ''
                                # positive_comment = ''
                                # negative_comment = ''
                                result = ''
                                for count in DiscourseLabel[clause_number]:
                                        EachPart = DiscourseLabel[clause_number][count]
                                        Discourse_flag = EachPart[2]
                                        # word_set = set(sentence[EachPart[0]:EachPart[1]])
                                        bagsPOS = sequence[EachPart[0]:EachPart[1]]
                                        contextFlag = 1
                                        for Eachword in bagsPOS:
                                                word = Eachword[0] + '-' + Eachword[1]
                                                # print(word)
                                                # sequence[index][0] + '-' + sequence[index][1]
                                                if word in Lexicon:
                                                        contextFlag = 0
                                                        break
                                        final = ((self.flag)^Discourse_flag)
                                        result = (' ' + ' '.join("%s#%s " % wordTagged for wordTagged in sequence[EachPart[0]:EachPart[1]]))
                                        result = result.strip()
                                        if not result:
                                                print('Empty context case\n', sentence)
                                                print(EachPart[0], EachPart[1])
                                                print(Marker_range_set)
                                                print('\n\n')
                                        stringToWrite = lineInit + middleFix + str(CurrentLine) + middleFix + str(clause_number) + middleFix + str(EachPart[0]) + middleFix + ' ' + result
                                        if contextFlag:
                                                if final:
                                                        self.Pfp.write(stringToWrite + '\n')
                                                        positive_case += 1
                                                else:
                                                        self.Nfp.write(stringToWrite + '\n')
                                                        negative_case += 1
                                        else:
                                                if final:
                                                        self.Pcomfp.write(stringToWrite + '\n')
                                                else:
                                                        self.Ncomfp.write(stringToWrite + '\n')
                                        # if not (word_set & Lexicon):
                                        #         sentence = ptree.leaves()
                                        #         final = ((self.flag)^Discourse_flag)
                                        #         if ((sentence[EachPart[0]] in initial_set) and ((EachPart[0] + 1) != EachPart[1])):
                                        #                 if final:
                                        #                         positive_part += (' ' + ' '.join(sentence[(EachPart[0] + 1):EachPart[1]]))
                                        #                 else:
                                        #                         negative_part += (' ' + ' '.join(sentence[(EachPart[0] + 1):EachPart[1]]))
                                        #         elif sentence[EachPart[0]] not in initial_set:
                                        #                 if final:
                                        #                         positive_part += (' ' + ' '.join(sentence[EachPart[0]:EachPart[1]]))
                                        #                 else:
                                        #                         negative_part += (' ' + ' '.join(sentence[EachPart[0]:EachPart[1]]))
                                
                                        total += 1
                                # if positive_part != '' and len(positive_part) > 10:
                                #         self.Pfp.write(positive_part + '\n')
                                #         positive_case += 1
                                # if negative_part != '' and len(negative_part) > 10:
                                #         self.Nfp.write(negative_part + '\n')
                                #         negative_case += 1
                        threadLock.release()
                        threadLock.acquire()
                        line = self.fp.readline()
                        CurrentLine = lineCount
                        lineCount += 1
                        while CurrentLine in self.BlackList:
                                line = self.fp.readline()
                                CurrentLine = lineCount
                                lineCount += 1
                        threadLock.release()

def Get_initial(path, initial_set):
        with open(path, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        temp = defaultdict(float)
                        arg1, arg2, _, temp['a'], temp['b'], temp['c'], temp['d'] = lines.rstrip().split(',')
                        if temp['c'] == max(temp.values()):
                                if arg1:
                                        initial_set.add(arg1)
                                if arg2:
                                        initial_set.add(arg2)

def ExtractContext(polarFlag, pos_parser_file, fp1, fp2, fp3, fp4, lexiconType, BlackList):
        global total
        global positive_case
        global negative_case
        global lineCount
        lineCount = 0
        total = 0
        positive_case = 0
        negative_case = 0
        thread_num = 24
        threads = []
        with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
                for x in range(0, thread_num + 1):
                        name = 'Thread-{}'.format(x)
                        thread = myThread(x + 1, name, x + 1, fp, fp1, fp2, fp3, fp4, polarFlag, lexiconType, BlackList)
                        thread.start()
                        threads.append(thread)

                # 等待所有线程完成
                for t in threads:
                        t.join()
                print ("Exiting Main Thread")
        print ("{}".format(pos_parser_file))
        # print ()
        # temp = 'total ' + str(total) + ',positive ' + str(positive_case) + ',negative ' + str(negative_case)
        # print (temp)
        print ('total IP-{}'.format(total))
        # print (positive_case)
        # print (negative_case) 
        print ('positive case is {} when using {} lexicon'.format(positive_case, lexiconType)) 
        print ('negative case is {} when using {} lexicon'.format(negative_case, lexiconType))
        # print(count)


def context_finding_discourse(argv): 
        sys.setrecursionlimit(2000)
        # global Lexicon 
        polarization = {'positive', 'negative'}
        extracting_set = {'training', 'testing'}
        # Address_lex = './experiment/Entry_processed/lexicon_build/'
        ParseResultAddress = './Entry_processed/Entry_fullparsing/'
        ContextOutputAddress = './Entry_processed/Context_Extracted/discourse/'
        CommentOutputAddress = './Entry_processed/Comment_Extracted/discourse/'
        BlackListAddress = './Entry_processed/DeleteList/'
        # for polar in polarization:
        #     fileName = Address_lex + 'voc_final_' + polar + '.txt'
        #     ReadInLexicon(Lexicon, fileName)
        prefix = 'FullPasingResult_Segmented_Entry_'
        lexicon_set = {'automatic_', 'manual_corrected_'}
        for postfix in extracting_set:
                for lexiconType in lexicon_set:
                        with open(ContextOutputAddress + 'Context_discourse_positive_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp1:
                                with open(ContextOutputAddress + 'Context_discourse_negative_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp2:
                                        # with open(ContextOutputAddress + 'Context_Fullparsing_discourse_positive_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp5:
                                        #         with open(ContextOutputAddress + 'Context_Fullparsing_discourse_negative_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp6:
                                        with open(CommentOutputAddress + 'Comment_discourse_positive_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp3:
                                                with open(CommentOutputAddress + 'Comment_discourse_negative_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp4:
                                                        for polar in polarization:
                                                                if polar == 'positive':
                                                                        polarFlag = 1
                                                                else:               # Read in the negative file
                                                                        polarFlag = 0
                                                                pos_parser_file = ParseResultAddress + prefix + polar + '_' + postfix + '.txt'
                                                                # ExtractContext(polarFlag, pos_parser_file, fp1, fp2, fp3, fp4, lexicon_set, fp5, fp6)
                                                                BlackList = set()
                                                                BlackListName = '{}Entry_{}_{}.txt'.format(BlackListAddress, polar, postfix)
                                                                ReadInBlackList(BlackList, BlackListName)
                                                                ExtractContext(polarFlag, pos_parser_file, fp1, fp2, fp3, fp4, lexiconType, BlackList)

if __name__ == '__main__':
        context_finding_discourse(sys.argv[1:])