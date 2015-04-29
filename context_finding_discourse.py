import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys
import threading

total = 0
positive_case = 0
negative_case = 0
threadLock = threading.Lock()

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, fp, fp1, fp2, flag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.fp = fp
        self.flag = flag
        self.Pfp = fp1
        self.Nfp = fp2
    def run(self):          #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        global total
        global positive_case
        global negative_case
        Lexicon = set()
        initial_set = set()
        polarization = {'positive','negative'}
        Address_lex = './experiment/Entry_processed/lexicon_build/'
        threadLock.acquire()
        Get_initial('./experiment/Entry_processed/connectives.csv', initial_set)
        for polar in polarization:
            fileName = Address_lex + 'voc_final_' + polar + '.txt'
            ReadInLexicon(Lexicon, fileName)
        detector = DiscourseMarker.LinkageDetector('./experiment/Entry_processed/connectives.csv')
        line = self.fp.readline()
        threadLock.release()        
        while line:
            line = line[:-1]
            if not line.startswith('(ROOT'):
                threadLock.acquire()
                line = self.fp.readline()
                threadLock.release()
                continue
            ptree = ParentedTree.fromstring(line)
            sentence = ptree.leaves()
            sequence = ptree.pos()
            Index = ptree.treepositions('leaves')
            IP_range = {}
            GetIPRange(ptree, IP_range)
            DiscourseLabel = defaultdict(dict)
            PriorityDecision(detector.detect_by_tokens(sentence), \
                IP_range, DiscourseLabel)
            for clause_number in DiscourseLabel:
                positive_part = ''
                negative_part = ''
                for count in DiscourseLabel[clause_number]:
                    EachPart = DiscourseLabel[clause_number][count]
                    Discourse_flag = EachPart[2]
                    word_set = set(sentence[EachPart[0]:EachPart[1]])
                    if not (word_set & Lexicon):
                        sentence = ptree.leaves()
                        final = ((self.flag)^Discourse_flag)
                        if ((sentence[EachPart[0]] in initial_set) and ((EachPart[0] + 1) != EachPart[1])):
                            if final:
                                positive_part += (' ' + ' '.join(sentence[(EachPart[0] + 1):EachPart[1]]))
                            else:
                                negative_part += (' ' + ' '.join(sentence[(EachPart[0] + 1):EachPart[1]]))
                        elif sentence[EachPart[0]] not in initial_set:
                            if final:
                                positive_part += (' ' + ' '.join(sentence[EachPart[0]:EachPart[1]]))
                            else:
                                negative_part += (' ' + ' '.join(sentence[EachPart[0]:EachPart[1]]))
                threadLock.acquire()
                total += 1
                if positive_part != '' and len(positive_part) > 10:
                    self.Pfp.write(positive_part + '\n')
                    positive_case += 1
                if negative_part != '' and len(negative_part) > 10:
                    self.Nfp.write(negative_part + '\n')
                    negative_case += 1
                threadLock.release()
            threadLock.acquire()
            line = self.fp.readline()
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

def PriorityFiltering(candidate, MarkerGroup):
    if not len(candidate):
        return
    if len(candidate) == 1:
        MarkerGroup.append(candidate.pop())
    workset = set()
    for x in range(0, len(candidate)):
        if set(candidate[x][1]) & workset:
            continue
        compare = candidate[x]
        workset |= set(compare[1])
        for y in range(x + 1, len(candidate)):
            temp = candidate[y]
            if set(temp[1]) & workset:
                workset |= set(temp[1])
                if temp[0] != compare[0]:
                    if compare[2] < temp[2]:    # Compare probability and decide the priority
                        compare = temp
        MarkerGroup.append(compare)

def FindPosition(position, IP_range_set, flag):         # flag = 0, front, flag = 1, after
    backup = -1
    for Each_head in IP_range_set:
        if (Each_head > int(position)) and flag:
            if backup == -1:
                backup = Each_head
            elif Each_head < backup:
                backup = Each_head
        elif (Each_head < int(position)) and (not flag):
            if backup == -1:
                backup = Each_head
            elif Each_head > backup:
                backup = Each_head
    return backup

def RangeModify(IP_range_set, MarkerGroup):
    if len(MarkerGroup) <= 1:
        return
    for x in range(0, len(MarkerGroup)):
        for y in range(x + 1, len(MarkerGroup)):
            if MarkerGroup[x][0][0] == MarkerGroup[y][0][0]:    # ('虽然', '') case
                left = FindPosition(MarkerGroup[x][1][1], IP_range_set, 1)
                right = FindPosition(MarkerGroup[y][1][1], IP_range_set, 1)
                if MarkerGroup[x][1][0] < MarkerGroup[y][1][0]:
                    if left < int(MarkerGroup[y][1][1]):
                        MarkerGroup[x] = ((MarkerGroup[x][0][0], MarkerGroup[x][0][1]), \
                            (int(MarkerGroup[x][1][0]), left), MarkerGroup[x][2])
                    else:
                        MarkerGroup[x] = ((MarkerGroup[x][0][0], MarkerGroup[x][0][1]), \
                            (int(MarkerGroup[x][1][0]), (int(MarkerGroup[y][1][1]) + 1)), MarkerGroup[x][2])
                else:
                    if right < int(MarkerGroup[x][1][1]):
                        MarkerGroup[y] = ((MarkerGroup[y][0][0], MarkerGroup[y][0][1]), \
                            (int(MarkerGroup[y][1][0]), left), MarkerGroup[y][2])
                    else:
                        MarkerGroup[y] = ((MarkerGroup[y][0][0], MarkerGroup[y][0][1]), \
                            (int(MarkerGroup[y][1][0]), (int(MarkerGroup[x][1][1]) + 1)), MarkerGroup[y][2])
            elif MarkerGroup[x][0][1] == MarkerGroup[y][0][1]:  # ('', '但是') case
                left = FindPosition(MarkerGroup[x][1][1], IP_range_set, 0)
                right = FindPosition(MarkerGroup[y][1][1], IP_range_set, 0)
                if MarkerGroup[x][1][1] > MarkerGroup[y][1][1]:
                    if left > int(MarkerGroup[y][1][1]):
                        MarkerGroup[x] = ((MarkerGroup[x][0][0], MarkerGroup[x][0][1]), \
                            (left, int(MarkerGroup[x][1][1])), MarkerGroup[x][2])
                    else:
                        MarkerGroup[x] = ((MarkerGroup[x][0][0], MarkerGroup[x][0][1]), \
                            ((int(MarkerGroup[y][1][1]) + 1), int(MarkerGroup[x][1][1])), MarkerGroup[x][2])
                else:
                    if right > int(MarkerGroup[x][1][1]):
                        MarkerGroup[y] = ((MarkerGroup[y][0][0], MarkerGroup[y][0][1]), \
                            (left, int(MarkerGroup[y][1][1])), MarkerGroup[y][2])
                    else:
                        MarkerGroup[y] = ((MarkerGroup[y][0][0], MarkerGroup[y][0][1]), \
                            ((int(MarkerGroup[x][1][1]) + 1), int(MarkerGroup[y][1][1])), MarkerGroup[y][2])

def GetIPHeadSet(IP_range_set, IP_range):
    for count in IP_range:
        IP_range_set.add(int(IP_range[count][0]))

def PriorityDecision(detected, IP_range, IP_range_label):       # previous_state = 0 same as label, = 1 reverse
    MarkerGroup = []
    candidate = list(detected)
    PriorityFiltering(candidate, MarkerGroup)
    IP_range_set = set()
    GetIPHeadSet(IP_range_set, IP_range)
    RangeModify(IP_range_set, MarkerGroup)
    previous_state = 0
    for IP_number in IP_range:
        temp = IP_range[IP_number]
        count = 0
        it = temp[0]
        for x in range(temp[0],temp[1]):
            flag = 0
            for everyMarker in MarkerGroup:
                if x in range(int(everyMarker[1][0]), int(everyMarker[1][1])):
                    flag = 1
                    if 1 != previous_state:
                        IP_range_label[IP_number][count] = (it, x, previous_state)
                        it = x
                        previous_state = 1
                        count += 1
                    break
            if not flag:
                if 0 != previous_state:
                    IP_range_label[IP_number][count] = (it, x, previous_state)
                    it = x
                    previous_state = 0
                    count += 1
        IP_range_label[IP_number][count] = (it, x + 1, previous_state)

def GetIPRange(ptree, IP_range):
    tree = ptree
    flag = 1
    while flag:
        for child in tree:
            if child.label() == 'ROOT':
                tree = child
                break
            if child != 'IP':
                flag = 0
                break
    count = 0
    it = 0
    for child in tree:
        if child.label() != 'PU':
            IP_range[count] = (it, it + len(child.leaves()))
            it += len(child.leaves())
            count += 1
        else:
            it += 1

def MiningFromText(flag, pos_parser_file, fp1, fp2):
    global total
    global positive_case
    global negative_case
    total = 0
    positive_case = 0
    negative_case = 0
    thread_num = 24
    threads = []
    with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
        for x in range(0, thread_num + 1):
            name = 'Thread-{}'.format(x)
            thread = myThread(x + 1, name, x + 1, fp, fp1, fp2, flag)
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
        print ('positive case-{}'.format(positive_case)) 
        print ('negative case-{}'.format(negative_case))
        # print(count)


# Lexicon = set()

def ReadInLexicon(Lexicon, fileName):
    fp = open(fileName , 'r', encoding = 'utf-8')
    for lines in fp:
        word = lines[:-1].split()[0]
        Lexicon.add(word)
    fp.close()

def context_finding_discourse(argv): 
    sys.setrecursionlimit(2000)
    # global Lexicon 
    polarization = {'positive','negative'}
    extracting_set = {'training','testing'}
    # Address_lex = './experiment/Entry_processed/lexicon_build/'
    ParseResultAddress = './experiment/Entry_processed/Entry_fullparsing/'
    OutputAddress = './experiment/Entry_processed/Context_Extracted/'
    # for polar in polarization:
    #     fileName = Address_lex + 'voc_final_' + polar + '.txt'
    #     ReadInLexicon(Lexicon, fileName)
    prefix = 'FullPasingResult_Segmented_Entry_'
    for postfix in extracting_set:
        with open(OutputAddress + 'Context_positive_' + postfix + '.txt', 'w', encoding = 'utf-8') as fp1:
            with open(OutputAddress + 'Context_negative_' + postfix + '.txt', 'w', encoding = 'utf-8') as fp2:
                for polar in polarization:
                    if polar == 'positive':
                        pos_parser_file = ParseResultAddress + prefix + polar + '_' + postfix + '.txt'
                        MiningFromText(1, pos_parser_file, fp1, fp2)
                    else:               # Read in the negative file
                        pos_parser_file = ParseResultAddress + prefix + polar + '_' + postfix + '.txt'
                        MiningFromText(0, pos_parser_file, fp1, fp2)


if __name__ == '__main__':
    context_finding_discourse(sys.argv[1:])