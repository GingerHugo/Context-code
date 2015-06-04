import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys

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
    detector = DiscourseMarker.LinkageDetector('G:/booking.com/Entry_processed/connectives.csv')
    with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
        count_line = 0
        for lines in fp:
            count_line += 1
            # print(count_line)
            line = lines[:-1]
            # print(line)
            if not line.startswith('(ROOT'):
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
            temp_list = list(detector.detect_by_tokens(sentence))
            if len(temp_list) > 5:
                print("\n\n\n")
                print(temp_list)
                print(sentence)
            PriorityDecision(detector.detect_by_tokens(sentence), \
                IP_range, DiscourseLabel)
            for clause_number in DiscourseLabel:
                for count in DiscourseLabel[clause_number]:
                    EachPart = DiscourseLabel[clause_number][count]
                    Discourse_flag = EachPart[2]
                    word_set = set()
                    for index in range(EachPart[0],EachPart[1]):
                        if sequence[index][1] in POSset:
                            TreePosition = Index[index]
                            leafIndex = tuple(TreePosition[x] \
                                for x in range(0 , len(TreePosition) - 1))
                            leaf = ptree[leafIndex]
                            # print(TreePosition)
                            # print(leafIndex)
                            if CheckVP(leaf):
                                Negatorflag = CheckNegator(leaf, negator_set)
                                final = (Negatorflag^flag^Discourse_flag)
                                if sequence[index][0] not in word_set:
                                    if final:
                                        EntryCount['positive'] += 1
                                        WordCount[sequence[index][0]]['positive'] += 1
                                    else:
                                        EntryCount['negative'] += 1
                                        WordCount[sequence[index][0]]['negative'] += 1
                                    word_set.add(sequence[index][0])


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
        negativeCase = WordCount[word].get('positive', 0)
        if (positiveCase + negativeCase) < threshold:
            continue
        if positiveCase and negativeCase:
            word_frequency = positiveCase + negativeCase
            left = log2((N * positiveCase) / (EntryCount['positive'] * word_frequency))
            right = log2((N * negativeCase) / (EntryCount['negative'] * word_frequency))
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

    Vocaddress = 'G:/booking.com/Entry_processed/lexicon_build/'
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
    for element in chi_square_result:
        pos_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    pos_chi_square.close()

    chi_square_result = neg_counter_chi_square.most_common()
    for element in chi_square_result:
        neg_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    neg_chi_square.close()


def BuildingDiscourse(argv):
    None_set = {"NR", "NT", "NN"}
    Verb_set = {"VA", "VC", "VE", "VV"}
    Advb_set = {"AD"}
    Adjc_set = {"JJ"}
    threshold = 10           # At least appears ten times
    POSset = Verb_set | Advb_set | Adjc_set
    EntryCount = Counter()
    WordCount = defaultdict(Counter)
    polarization = {'positive','negative'}
    ParseResultAddress = 'G:/booking.com/Entry_processed/Entry_fullparsing/'
    negator_set = set()
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
    BuildingDiscourse(sys.argv[1:])