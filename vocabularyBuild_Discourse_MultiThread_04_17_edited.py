import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys
import threading


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, fp, flag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.fp = fp
        self.flag = flag
    def run(self):          #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        global POSset
        global EntryCount
        global WordCount
        global negator_set
        threadLock.acquire()
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
            PriorityDecision(detector.detect_by_tokens(sentence), \
                IP_range, DiscourseLabel, ptree)
            for clause_number in DiscourseLabel:
                for count in DiscourseLabel[clause_number]:
                    EachPart = DiscourseLabel[clause_number][count]
                    Discourse_flag = EachPart[2]
                    word_set = set()
                    for index in range(EachPart[0], EachPart[1]):
                        if sequence[index][1] in POSset:
                            TreePosition = Index[index]
                            leafIndex = tuple(TreePosition[x] \
                                for x in range(0 , len(TreePosition) - 1))
                            leaf = ptree[leafIndex]
                            # print(TreePosition)
                            # print(leafIndex)
                            if CheckVP(leaf):
                                Negatorflag = CheckNegator(leaf, negator_set)
                                final = (Negatorflag^(self.flag)^Discourse_flag)
                                if sequence[index][0] not in word_set:
                                    threadLock.acquire()
                                    if final:
                                        EntryCount['positive'] += 1
                                        WordCount[sequence[index][0]]['positive'] += 1
                                    else:
                                        EntryCount['negative'] += 1
                                        WordCount[sequence[index][0]]['negative'] += 1
                                    word_set.add(sequence[index][0])
                                    threadLock.release()
            threadLock.acquire()
            line = self.fp.readline()
            threadLock.release()

def PriorityFiltering(candidate, MarkerGroup):
    if not len(candidate):
        return
    if len(candidate) == 1:
        MarkerGroup.append(candidate.pop())
    workset = set()
    candidate.sort(key=lambda t: t[2])
    while len(candidate):
        temp = candidate.pop()
        if (set(temp[1]) & workset) and (temp[0][0] and temp[0][1]):
            continue
        elif (set(temp[1][1]) & workset) and (temp[0][1]):      # '___,但是' case
            continue
        elif (set(temp[1][0]) & workset) and (temp[0][0]):      # '虽然,___' case
            continue
        else:
            for x in range(-1,-(len(candidate) + 1),-1):
                # Using probability as filtering criteria
                if candidate[x][2] < temp[2]:
                    workset |= set(temp[1])
                    MarkerGroup.append(temp)
                    break
                # Pick the nearest marker
                elif (candidate[x][1][0] == temp[1][0]) and (candidate[x][1][1] < temp[1][1]) and (temp[0][1]):
                    temp = candidate[x]
                elif (candidate[x][1][1] == temp[1][1]) and (candidate[x][1][0] > temp[1][0]) and (temp[0][0]):
                    temp = candidate[x]

def SeekVP(leaf, direction):
    EndingSet = {'IP','VP','ROOT'}
    offset = 0
    flag = 2 * direction - 1
    while 1:
        if direction:
            if not leaf.right_sibling():
                leaf = leaf.parent()
                continue
            leaf = leaf.right_sibling()
        else:
            if not leaf.left_sibling():
                leaf = leaf.parent()
                continue
            leaf = leaf.left_sibling()
        if leaf.label() == 'PU':
            offset += (1 * flag)
            continue
        offset += (len(leaf.leaves()) * flag)
        if leaf.label() in EndingSet:
            offset += (1 * flag)
            return offset
        for subtree in leaf.subtrees(lambda t: t.label() in EndingSet):
            offset += (1 * flag * direction) 
            return offset

def GetSingleMarkerRange(temp, ptree, IP_range_set):
    Index = ptree.treepositions('leaves')
    sentenceLength = len(ptree.leaves())
    if temp[0][0]:          # ('虽然', '') case
        position = temp[1][0]
    else:                   # ('', '但是') case
        position = temp[1][1]
    left = 0
    right = sentenceLength
    if position in IP_range_set:      # In the head of one main IP
        for y in IP_range_set:
            if (y > position) and (y < right):
                right = y
            elif (y < position) and (y > left):
                left = y
        right -= 1
        return(left, position, right)
    else:                           # In the IP
        TreePosition = Index[position]
        leafIndex = tuple(TreePosition[x] \
            for x in range(0 , len(TreePosition) - 1))
        leaf = ptree[leafIndex]
        offset = SeekVP(leaf, 1)
        right = position + offset
        if temp[0][1]:              # ('', '但是') case
            offset = SeekVP(leaf, 0)
            left = position + offset
        return(left, position, right)

def RangeModify(IP_range_set, MarkerGroup, Marker_range_set, ptree):
    if len(MarkerGroup) <= 1:
        return
    singleMarkerPool = []
    sentenceLength = len(ptree.leaves())
    for x in range(0, len(MarkerGroup)):
        temp = MarkerGroup[x]
        if (not temp[0][0]) or (not temp[0][1]):
            singleMarkerPool.append(temp)
            continue
        if set(range(int(temp[1][0]), int(temp[1][1]))) & Marker_range_set:
            if int(temp[1][0]) not in Marker_range_set:         # head is not in the range
                for x in range(int(temp[1][0]), int(temp[1][1])):
                    if x in Marker_range_set:
                        break
                    else:
                        Marker_range_set |= {x}
            if int(temp[1][1]) in Marker_range_set:             # tail is in the range
                for x in range(int(temp[1][1]), sentenceLength):
                    if x in Marker_range_set:
                        Marker_range_set -= {x}
                    else:
                        break
        else:                           # no overlap add directly
            Marker_range_set |= set(range(int(temp[1][0]), int(temp[1][1])))
    if not singleMarkerPool:
        for x in range(0, len(singleMarkerPool)):
            temp = MarkerGroup[x]
            rangeSingleMarkerTemp = GetSingleMarkerRange(temp, ptree, IP_range_set)
            if not temp[0][0]:      # ('虽然', '') case
                left = rangeSingleMarkerTemp[1]
                right = rangeSingleMarkerTemp[2]
                ending = sentenceLength
            else:                   # ('', '但是') case
                left = rangeSingleMarkerTemp[0]
                right = rangeSingleMarkerTemp[1]
                ending = rangeSingleMarkerTemp[2]
            if set(range(int(left), int(right))) & Marker_range_set:
                if int(left) not in Marker_range_set:                   # head is not in the range
                    for x in range(left, right):
                        if x in Marker_range_set:
                            break
                        else:
                            Marker_range_set |= {x}
                if (int(right) in Marker_range_set) and temp[0][1]:     # tail is in the range and ('', '但是') case
                    for x in range(right, ending):
                        if x in Marker_range_set:
                            Marker_range_set -= {x}
                        else:
                            break
            else:                                                       # no overlap add directly
                Marker_range_set |= set(range(int(left), int(right)))

def GetIPHeadSet(IP_range_set, IP_range):
    for count in IP_range:
        IP_range_set.add(int(IP_range[count][0]))

def PriorityDecision(detected, IP_range, IP_range_label, ptree):       # previous_state = 0 same as label, = 1 reverse
    MarkerGroup = []
    candidate = list(detected)      # detected is a list of tuples which contains (marker, pair range, probability) 
    PriorityFiltering(candidate, MarkerGroup)
    IP_range_set = set()
    Marker_range_set = set()
    GetIPHeadSet(IP_range_set, IP_range)
    RangeModify(IP_range_set, MarkerGroup, Marker_range_set, ptree)
    previous_state = 0
    for IP_number in IP_range:
        temp = IP_range[IP_number]
        count = 0
        it = temp[0]
        for x in range(temp[0],temp[1]):
            flag = 0
            for everyMarker in MarkerGroup:
                if x in Marker_range_set:
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
    # Dive into the tree
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
    # Traverse the tree
    for child in tree:
        if child.label() != 'PU':
            IP_range[count] = (it, it + len(child.leaves()))
            it += len(child.leaves())
            count += 1
        else:
            it += 1

def ReadInNegator(negator_set, path):
    with open(path, 'r', encoding = 'utf-8') as fp:
        for line in fp:
            negator_set.add(line[:-1])

def CheckNegator(leaf, negator_set):
    flag = 0
    if leaf.left_sibling() and leaf.left_sibling().label() != 'PU':
        temp = leaf.left_sibling()
        if set(temp.leaves()) & negator_set:
            flag = flag^1
        else:
            flag = flag^0
        if temp.left_sibling() and temp.left_sibling().label() != 'PU':
            tmp = temp.left_sibling()
            if set(tmp.leaves()) & negator_set:
                flag = flag^1
            else:
                flag = flag^0
            return flag
        else:
            return flag
    else:
        return flag

def CheckVP(leaf):
    Plabel = leaf.parent().label()
    while Plabel != 'IP' and Plabel != 'ROOT':
        if Plabel == 'VP':
            return 1
        else:
            leaf = leaf.parent()
            # print(leaf)
            Plabel = leaf.label()
            # print(Plabel)
    return 0

def MiningFromText(flag, pos_parser_file, POSset, negator_set, EntryCount, WordCount):
    thread_num = 24
    threads = []
    with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
        for x in range(0, thread_num + 1):
            name = 'Thread-{}'.format(x)
            thread = myThread(x + 1, name, x + 1, fp, flag)
            thread.start()
            threads.append(thread)

        # 等待所有线程完成
        for t in threads:
            t.join()
        print ("Exiting Main Thread")
        # print(count)
            

def Calculation(package, threshold, EntryCount, WordCount):
    # Calculating the vocabulary value
    counter_st_1 = Counter()
    neg_counter_st_1 = Counter()
    counter_st_2 = Counter()
    neg_counter_st_2 = Counter()
    counter_st_3 = Counter()
    neg_counter_st_3 = Counter()
    pure_positive = Counter()
    pure_nagetive = Counter()
    counter_chi_square = Counter()
    neg_counter_chi_square = Counter()
    N = EntryCount['positive'] + EntryCount['negative']
    Total_word_list = Counter()

    # print('positive_word_total', positive_word_total)
    # print('negative_word_total', negative_word_total)

    for word in WordCount:
        positiveCase = WordCount[word].get('positive', 0)
        negativeCase = WordCount[word].get('negative', 0)
        if (positiveCase + negativeCase) < threshold:
            continue
        if positiveCase and negativeCase:
            word_frequency = positiveCase + negativeCase
            left = positiveCase * log2((N * positiveCase) / (EntryCount['positive'] * word_frequency))
            right = negativeCase * log2((N * negativeCase) / (EntryCount['negative'] * word_frequency))
            counter_st_1[word] = round(left, 4)
            counter_st_2[word] = round((positiveCase / EntryCount['positive']) / (negativeCase / EntryCount['negative']), 4)
            counter_st_3[word] = round(positiveCase / word_frequency, 4)
            neg_counter_st_1[word] = round(right, 4)
            neg_counter_st_2[word] = round((negativeCase / EntryCount['negative']) / (positiveCase / EntryCount['positive']), 4)
            neg_counter_st_3[word] = round(negativeCase / word_frequency, 4)
        else:
            if positiveCase:
                pure_positive[word] = WordCount[word]['positive']
            else:
                pure_nagetive[word] = WordCount[word]['negative']
        N_11 = positiveCase
        N_10 = negativeCase
        N_01 = EntryCount['positive'] - positiveCase
        N_00 = EntryCount['negative'] - negativeCase
        counter_chi_square[word] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)
        neg_counter_chi_square[word] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)
    total = (counter_st_1, counter_st_2, counter_st_3, counter_chi_square, neg_counter_st_1, neg_counter_st_2, neg_counter_st_3, neg_counter_chi_square, pure_positive, pure_nagetive)
    for x in range(0, len(total)):
        package.append(total[x])

def OutputResult(package):
    counter_st_1 = package[0]
    counter_st_2 = package[1] 
    counter_st_3 = package[2] 
    counter_chi_square = package[3] 
    neg_counter_st_1 = package[4] 
    neg_counter_st_2 = package[5] 
    neg_counter_st_3 = package[6]
    neg_counter_chi_square = package[7]
    pure_positive = package[8]
    pure_nagetive = package[9]

    Vocaddress = './experiment/Entry_processed/lexicon_build/'
    positive_voc_name_1 = 'voc_positive_MI.txt'
    negative_voc_name_1 = 'voc_negative_MI.txt'
    pos_voc_1 = open(Vocaddress + positive_voc_name_1, 'w', encoding = 'utf-8')
    neg_voc_1 = open(Vocaddress + negative_voc_name_1, 'w', encoding = 'utf-8')
    positive_voc_name_2 = 'voc_positive_Log.txt'
    negative_voc_name_2 = 'voc_negative_Log.txt'
    pos_voc_2 = open(Vocaddress + positive_voc_name_2, 'w', encoding = 'utf-8')
    neg_voc_2 = open(Vocaddress + negative_voc_name_2, 'w', encoding = 'utf-8')
    positive_voc_name_3 = 'voc_positive_RR.txt'
    negative_voc_name_3 = 'voc_negative_RR.txt'
    pos_voc_3 = open(Vocaddress + positive_voc_name_3, 'w', encoding = 'utf-8')
    neg_voc_3 = open(Vocaddress + negative_voc_name_3, 'w', encoding = 'utf-8')
    positive_chi_square_name = 'voc_chi_square_positive.txt'
    negative_chi_square_name = 'voc_chi_square_negative.txt'
    pos_chi_square = open(Vocaddress + positive_chi_square_name, 'w', encoding = 'utf-8')
    neg_chi_square = open(Vocaddress + negative_chi_square_name, 'w', encoding = 'utf-8')
    fileList = [pos_voc_1, pos_voc_2, pos_voc_3]
    result = [counter_st_1, counter_st_2, counter_st_3]
    for x in range(0,3):
        posTemp = pure_positive.most_common()
        fileList[x].write('Absolute positive word: \n')
        for element in posTemp:
            fileList[x].write(element[0] + ' ' + str(element[1]) + '\n')
        fileList[x].write('\nNon-absolute positive word: \n')
        posTemp = result[x].most_common()
        for element in posTemp:
            fileList[x].write(element[0] + ' ' + str(element[1]) + '\n')
        fileList[x].close()
    fileList = [neg_voc_1, neg_voc_2, neg_voc_3]
    result = [neg_counter_st_1, neg_counter_st_2, neg_counter_st_3]
    for x in range(0,3):
        negTemp = pure_nagetive.most_common()
        fileList[x].write('Absolute negative word: \n')
        for element in negTemp:
            fileList[x].write(element[0] + ' ' + str(element[1]) + '\n')
        fileList[x].write('\nNon-absolute negative word: \n')
        negTemp = result[x].most_common()
        for element in negTemp:
            fileList[x].write(element[0] + ' ' + str(element[1]) + '\n')
        fileList[x].close()

    chi_square_result = counter_chi_square.most_common()
    pos_chi_square.write('Absolute positive word: \n')
    pos_chi_square.write('\nNon-absolute positive word: \n')
    for element in chi_square_result:
        pos_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    pos_chi_square.close()

    chi_square_result = neg_counter_chi_square.most_common()
    neg_chi_square.write('Absolute negative word: \n')
    neg_chi_square.write('\nNon-absolute negative word: \n')
    for element in chi_square_result:
        neg_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    neg_chi_square.close()

POSset = set()
EntryCount = Counter()
WordCount = defaultdict(Counter)
negator_set = set()
threadLock = threading.Lock()

def BuildingDiscourse_Multi(argv): 
    sys.setrecursionlimit(2000)   
    global POSset
    global EntryCount
    global WordCount
    global negator_set
    None_set = {"NR", "NT", "NN"}
    Verb_set = {"VA", "VC", "VE", "VV"}
    Advb_set = {"AD"}
    Adjc_set = {"JJ"}
    threshold = 10           # At least appears ten times
    POSset = Verb_set | Advb_set | Adjc_set
    polarization = {'positive','negative'}
    ParseResultAddress = './experiment/Entry_processed/Entry_fullparsing/'
    path = './negator.txt'
    ReadInNegator(negator_set, path)
    # mutex = multiprocessing.RLock()       # mutex lock of multi-threading
    prefix = 'FullPasingResult_Segmented_Entry_'
    for polar in polarization:
        if polar == 'positive':
            pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
            MiningFromText(1, pos_parser_file, POSset, negator_set, EntryCount, WordCount)
        else:               # Read in the negative file
            pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
            MiningFromText(0, pos_parser_file, POSset, negator_set, EntryCount, WordCount)
    package = []
    Calculation(package, threshold, EntryCount, WordCount)
    OutputResult(package)


if __name__ == '__main__':
    BuildingDiscourse_Multi(sys.argv[1:])