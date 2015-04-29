import string  
import re  
import sys
import os
from collections import *
from math import *
# from multiprocessing import mutex
# import multiprocessing               # may get overwritten


positive_opi = Counter()
negative_opi = Counter()
positive_word_total = 0
negative_word_total = 0
aspect = Counter()
aspect_count = Counter()
count_pos = 0
count_neg = 0
# counting = defaultdict(lambda: defaultdict(str))
None_set = {"NR", "NT", "NN"}
Verb_set = {"VA", "VC", "VE", "VV"}
AdVb_set = {"AD"}
Adjc_set = {"JJ"}
threshold = 5           # At least appears five times

def strQ2B(ustring):
    """把字符串全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code==0x3000:
            inside_code=0x0020
        else:
            inside_code-=0xfee0
        if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符返回原来的字符
            rstring += uchar
        else:
            rstring += chr(inside_code)
    return rstring

def strB2Q(ustring):
    """把字符串半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符就返回原来的字符
            rstring += uchar
        else:
            if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
                inside_code=0x3000
            else:
                inside_code+=0xfee0
            rstring += chr(inside_code)
    return rstring

def GetTotalNumber(cityList, ParseResultAddress):
    global count_pos
    global count_neg
    for city in cityList:
        pos_parser_file = ParseResultAddress + city + '_positive_seg.out.parse_result_positive' + city + '.1000.stp'
        neg_parser_file = ParseResultAddress + city + '_negative_seg.out.parse_result_negative' + city + '.1000.stp'
        pos_parser = open(pos_parser_file,'r',encoding = 'utf-8')
        neg_parser = open(neg_parser_file,'r',encoding = 'utf-8')
        for lines in pos_parser:
            line = lines[:-1]
            if line:
                pass
            else:
                count_pos += 1
        pos_parser.close()
        for lines in neg_parser:
            line = lines[:-1]
            if line:
                label = line.split('(')[0]
            else:
                count_neg += 1
        neg_parser.close()

def BuildingTheVocab(flag, parser_file_address, pos_file_address, neg):
    global None_set
    global Verb_set
    global AdVb_set
    global Adjc_set
    # global counting
    global positive_word_total
    global negative_word_total
    global positive_opi
    global negative_opi
    global count_pos
    global count_neg
    global aspect_count

    stopList = {'－－－－－','－'}

    # relationCollection = {'assmod':1, 'nsubj':1, 'nn':1, 'dobj':1, }
    parserFile = open(parser_file_address,'r',encoding = 'utf-8')  
    posFile = open(pos_file_address, 'r', encoding = 'utf-8')
    for lines in posFile:
        vote = 0
        lines = lines[:-1]
        bagOfWords = lines.split()
        wordbags = {}
        NounBags = {}
        # relationTemp = {}
        POSMapping = {}
        CandidateRelationTemp = {}
        POSMapping['ROOT'] = 'ROOT'
        for words in bagOfWords:
            Word_Candidate = words.rpartition('#')[0]
            Word_Candidate = strB2Q(Word_Candidate)
            POS_tag = words.rpartition('#')[2]
            POSMapping[Word_Candidate] = POS_tag
            if (POS_tag in Verb_set) or (POS_tag in AdVb_set) or (POS_tag in Adjc_set):
                if Word_Candidate not in stopList:
                    wordbags[Word_Candidate] = 1
            elif POS_tag in None_set:
                if Word_Candidate not in stopList:
                    NounBags[Word_Candidate] = 1
        lines = parserFile.readline()
        line = lines[:-1]
        while line:
            # if line.split('(')[0] in relationCollection:
            righWord = line.split()[1].split('-')[0]
            leftWord = line.split('(')[1].split('-')[0]
            relation_parser = line.split('(')[0]
            if (leftWord in wordbags) or (leftWord in NounBags):
                if righWord not in POSMapping:
                    print(righWord)
                else:
                    CandidateRelationTemp.setdefault(leftWord,{})[POSMapping[righWord]] = relation_parser
            if righWord in wordbags or righWord in NounBags:
                if leftWord not in POSMapping:
                    print(leftWord)
                else:
                    CandidateRelationTemp.setdefault(righWord,{})[POSMapping[leftWord]] = relation_parser
            lines = parserFile.readline()
            line = lines[:-1]

        for word in wordbags:
            if word not in CandidateRelationTemp:
                print (CandidateRelationTemp)
                print(wordbags)
                print(word)
                continue
            tempList = CandidateRelationTemp[word]
            word = strQ2B(word)     # Return to 半角
            reverseFlag = 1
            if not set(tempList.keys()) & neg:
                reverseFlag = 0
            if set(tempList.keys()) & None_set:
                if not reverseFlag:
                    if flag:    # positive case
                        positive_opi[word] += 1
                        vote += 1
                    else:       # negative case
                        negative_opi[word] += 1
                        vote -= 1
                else:
                    if flag:    # positive case
                        negative_opi[word] += 1
                        vote -= 1
                    else:       # negative case
                        positive_opi[word] += 1
                        vote += 1
        for word in NounBags:
            if word not in CandidateRelationTemp:
                print (CandidateRelationTemp)
                print(wordbags)
                print(word)
                continue
            tempList = CandidateRelationTemp[word]
            word = strQ2B(word)     # Return to 半角
            if (set(tempList.keys()) & Adjc_set) or (set(tempList.keys()) & AdVb_set) or (set(tempList.keys()) & Verb_set):
                aspect_count[word] += 1
        if (flag > 0) and (vote < 0): # positive case
            positive_word_total -= 1
            negative_word_total += 1
        elif (flag <= 0) and (vote >= 0):       # negative case
            positive_word_total += 1
            negative_word_total -= 1
    posFile.close()
    parserFile.close()

def Calculation():
    global positive_word_total
    global negative_word_total
    global positive_opi
    global negative_opi
    global count_pos
    global count_neg
    global threshold


    # Calculating the vocabulary value
    counter_st_1 = Counter()
    neg_counter_st_1 = Counter()
    counter_st_2 = Counter()
    neg_counter_st_2 = Counter()
    counter_st_3 = Counter()
    neg_counter_st_3 = Counter()
    counter_chi_square = Counter()
    neg_counter_chi_square = Counter()
    # neg_counter_st_4 = Counter()
    pure_positive = Counter()
    pure_nagetive = Counter()
    N = count_pos + count_neg
    Total_word_list = Counter()

    # Method 1,2,3(positive)
    for words in positive_opi:
        if positive_opi[words] > threshold:
            Total_word_list[words] = 1
            if words in negative_opi:
                word_frequency = positive_opi[words] + negative_opi[words]
                left = log2((N * positive_opi[words]) / (positive_word_total * word_frequency))
                right = (negative_word_total - negative_opi[words]) * log2((N * (negative_word_total - negative_opi[words])) / (negative_word_total * (N - negative_opi[words] - positive_opi[words]))) / N
                counter_st_1[words] = round((left + right), 4)
                counter_st_2[words] = round((positive_opi[words] / positive_word_total) / (negative_opi[words] / negative_word_total), 4)
                counter_st_3[words] = round((positive_opi[words]) / word_frequency, 4)
            else:
                pure_positive[words] = positive_opi[words]
                # print('Absolute positive word!!',words)

    # Method 1,2,3(negative)
    for words in negative_opi:
        if negative_opi[words] > threshold:
            Total_word_list[words] = 1
            if words in positive_opi:
                word_frequency = positive_opi[words] + negative_opi[words]
                left = log2((N * negative_opi[words]) / (negative_word_total * word_frequency))
                right = (positive_word_total - positive_opi[words]) * log2((N * (positive_word_total - positive_opi[words])) / (positive_word_total * (N - negative_opi[words] - positive_opi[words]))) / N
                neg_counter_st_1[words] = round((left + right), 4)
                # neg_counter_st_1[words] = round(negative_opi[words] * (log2(negative_opi[words] / ((negative_word_total[words] * (positive_opi[words] + negative_opi[words])) / (count_pos + count_neg)))), 4)
                neg_counter_st_2[words] = round((negative_opi[words] / negative_word_total) / (positive_opi[words] / positive_word_total), 4)
                neg_counter_st_3[words] = round((negative_opi[words]) / word_frequency, 4)
            else:
                pure_nagetive[words] = negative_opi[words]
                # print('Absolute negative word!!',words)

    # Method 4(Chi-square)
    for words in Total_word_list:
        N_11 = positive_opi[words]
        N_10 = negative_opi[words]
        if (N_11 > threshold) or (N_10 > threshold):
            N_01 = positive_word_total - positive_opi[words]
            N_00 = negative_word_total - negative_opi[words]
            # E_11 = (N_11 + N_10) * (N_11 + N_01) / N
            # E_10 = (N_11 + N_10) * (N_10 + N_00) / N
            # E_01 = (N_11 + N_01) * (N_01 + N_00) / N
            # E_00 = (N_01 + N_00) * (N_10 + N_00) / N
            # counter_chi_square[words] = round(((pow((N_11 - E_11),2) / E_11) + (pow((N_00 - E_00),2) / E_00)), 4)
            # neg_counter_chi_square[words] = round(((pow((N_10 - E_10),2) / E_10) + (pow((N_01 - E_01),2) / E_01)), 4)
            counter_chi_square[words] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)
            neg_counter_chi_square[words] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)


    package = (counter_st_1, counter_st_2, counter_st_3, counter_chi_square, neg_counter_st_1, neg_counter_st_2, neg_counter_st_3, neg_counter_chi_square, pure_positive, pure_nagetive)
    return package

def OutputResult(package):
    global aspect_count
    global threshold
    
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

    Vocaddress = 'G:/booking.com/training/'
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
    aspect_file_name = 'aspect_extracted.txt'
    aspect_file = open(Vocaddress + aspect_file_name, 'w', encoding = 'utf-8')
    fileList = [pos_voc_1, pos_voc_2, pos_voc_3]
    result = [counter_st_1, counter_st_2, counter_st_3]
    for x in range(0,3):
        posTemp = pure_positive.most_common()
        fileList[x].write('Absolute positive word: \n')
        # print (posTemp)
        for element in posTemp:
            # print (element)
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
    posTemp = pure_positive.most_common()
    pos_chi_square.write('Absolute positive word: \n')
    for element in posTemp:
        pos_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    pos_chi_square.write('\nNon-absolute positive word: \n')
    for element in chi_square_result:
        pos_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    pos_chi_square.close()

    chi_square_result = neg_counter_chi_square.most_common()
    negTemp = pure_nagetive.most_common()
    neg_chi_square.write('Absolute negative word: \n')
    for element in negTemp:
        neg_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    neg_chi_square.write('\nNon-absolute negative word: \n')
    for element in chi_square_result:
        neg_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
    neg_chi_square.close()

    aspect_result = aspect_count.most_common()
    for element in aspect_result:
        if element[1] > threshold:
            aspect_file.write(element[0] + ' ' + str(element[1]) + '\n')
    aspect_file.close()


def BuildingMain(argv):
    global positive_word_total
    global negative_word_total
    global count_pos
    global count_neg
    cityList1 = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList2 = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian']
    cityList3 = ['Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan','Paris']
    cityList4 = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore','Kunming']
    cityList5 = ['Huangshan','Jiuzhaigou','Guiyang','Chongqing','Rome','Barcelona']
    cityList6 = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane']
    cityList7 = ['GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = cityList1 + cityList2 + cityList3 + cityList4 + cityList5 + cityList6 + cityList7
    ParseResultAddress = 'G:/booking.com/parseResult/'
    GetTotalNumber(cityList, ParseResultAddress)
    neg = {'没','不','没有','不太','不够'}
    POSaddress = 'G:/booking.com/postagged/'
    positive_word_total = count_pos
    negative_word_total = count_neg
    # mutex = multiprocessing.RLock()       # mutex lock of multi-threading
    for city in cityList:
        # Read in the positive file
        pos_parser_file = ParseResultAddress + city + '_positive_seg.out.parse_result_positive' + city + '.1000.stp'   
        positive_file_name = city + '_positive_pos.out'
        pos_file_address = POSaddress + positive_file_name
        BuildingTheVocab(1, pos_parser_file, pos_file_address, neg)

        # Read in the negative file
        neg_parser_file = ParseResultAddress + city + '_negative_seg.out.parse_result_negative' + city + '.1000.stp'
        negative_file_name = city + '_negative_pos.out'
        pos_file_address = POSaddress + negative_file_name
        BuildingTheVocab(0, neg_parser_file, pos_file_address, neg)
    package = Calculation()
    OutputResult(package)

if __name__ == '__main__':
    BuildingMain(sys.argv[1:])