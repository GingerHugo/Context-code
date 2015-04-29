import string  
import re  
import sys
import os
from collections import *
from math import *

Ending_dict = {'。#PU':1, '！#PU':2, '!#PU':3,'?#PU':4,'.#PU':5,'？#PU':6}
Transition_dict = {'，#PU':1,',#PU':2}

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


cityList1 = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
cityList2 = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
cityList3 = ['Paris']
cityList4 = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore','Kunming','Huangshan','Jiuzhaigou','Guiyang','Chongqing','Rome','Barcelona']
AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
cityList5 = AList
cityList = cityList1 + cityList2 + cityList3 + cityList4 + cityList5
# cityList = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']

POSaddress = 'G:/booking.com/postagged/'
Vocaddress = 'G:/booking.com/training/'
# Paraddress = 
ParseResultAddress = 'G:/booking.com/parseResult/'
positive_opi = Counter()
negative_opi = Counter()
positive_word_total = Counter()
negative_word_total = Counter()
aspect = Counter()
positive_total_word = 0
negative_total_word = 0
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

neg = {}
count_pos = 0
count_neg = 0

for city in cityList:
    pos_parser_file = ParseResultAddress + city + '_positive_seg.out.parse_result_positive' + city + '.1000.stp'
    neg_parser_file = ParseResultAddress + city + '_negative_seg.out.parse_result_negative' + city + '.1000.stp'
# 'G:/booking.com/parseResult/old-full-parsing/Guangzhou_negative_seg.out.parse_result_negativeGuangzhou.1000.stp'
# neg_parser_file = 'G:/booking.com/parseResult/old-full-parsing/Guangzhou_positive_seg.out.parse_result_positiveGuangzhou.1000.stp'
    pos_parser = open(pos_parser_file,'r',encoding = 'utf-8')
    neg_parser = open(neg_parser_file,'r',encoding = 'utf-8')

    for lines in pos_parser:
        line = lines[:-1]
        if line:
            label = line.split('(')[0]
            if label == 'neg':
                neg[line.split()[1].split('-')[0]] = 1
                # if line.split()[1].split('-')[0] == '简直' or line.split()[1].split('-')[0] == '几乎':
                    # print(line)
        else:
            count_pos += 1
    pos_parser.close()
    # print(city,'positive',count_pos)

    for lines in neg_parser:
        line = lines[:-1]
        if line:
            label = line.split('(')[0]
            if label == 'neg':
                neg[line.split()[1].split('-')[0]] = 1
        else:
            count_neg += 1
    neg_parser.close()
# print(neg)

counting = defaultdict(lambda: defaultdict(str))

def BuildingTheVocab(flag, pos_parser_file, pos_file_address):
    global counting
    global positive_word_total
    global negative_word_total
    global positive_opi
    global negative_opi


    # POSaddress = 'G:/booking.com/postagged/'
    neg = {'没': 1, '不': 1, '没有': 1}
    neg['不太'] = 1
    neg['不够'] = 1
    relationCollection = {'assmod':1, 'nsubj':1, 'nn':1, 'dobj':1, }
    pos_parser = open(pos_parser_file,'r',encoding = 'utf-8')
    # neg_parser = open(neg_parser_file,'r',encoding = 'utf-8')
    
    postive_file = open(pos_file_address, 'r', encoding = 'utf-8')
    for lines in postive_file:
        lines = lines[:-1]
        bagOfWords = lines.split()
        wordbags = {}
        NounBags = {}
        relationTemp = {}
        CandidateRelationTemp = {}
        for words in bagOfWords:
            if words.split('#')[1] == 'VA' or words.split('#')[1] == 'JJ' or words.split('#')[1] == 'AD' or words.split('#')[1] == 'VV':
                wordbags[words.split('#')[0]] = 1
            elif words.split('#')[1] == 'NN': 
                NounBags[words.split('#')[0]] = 1
        lines = pos_parser.readline()
        line = lines[:-1]
        while line:
            if line.split('(')[0] in relationCollection:
                CandidateRelationTemp.setdefault(line.split()[1].split('-')[0],{})[line.split('(')[1].split('-')[0]] = line.split('(')[0]
                CandidateRelationTemp.setdefault(line.split('(')[1].split('-')[0],{})[line.split()[1].split('-')[0]] = line.split('(')[0]
            relationTemp.setdefault(line.split()[1].split('-')[0],{})[line.split('(')[1].split('-')[0]] = 1
            relationTemp.setdefault(line.split('(')[1].split('-')[0],{})[line.split()[1].split('-')[0]] = 1
            lines = pos_parser.readline()
            line = lines[:-1]
        for word in wordbags:
            half_flag = 0
            if word not in relationTemp:
                half_flag = 1
                word_2 = strB2Q(word)
                if word_2 not in relationTemp:
                    print(word_2)
                    continue
                else:
                    word = word_2
            tempList = relationTemp[word]
            if half_flag:
                word = strQ2B(word)
                half_flag = 0
            reverseFlag = 0
            for everyAttach in tempList:
                # everyAttach is the linkage in Dependency Parser
                if everyAttach in neg:
                    reverseFlag = 1
                    break
            if word not in CandidateRelationTemp:
                half_flag = 1
                word_2 = strB2Q(word)
                if word_2 not in CandidateRelationTemp:
                    # print(word_2)
                    continue
                else:
                    word = word_2
            candidate = CandidateRelationTemp[word]
            if not reverseFlag:
                if flag:    # positive case
                    for target in candidate:
                        if candidate[target] != 'nn':
                            positive_opi[word] += 1
                            if not positive_word_total[word]:
                                positive_word_total[word] = count_pos
                                negative_word_total[word] = count_neg
                else:       # negative case
                    for target in candidate:
                        if candidate[target] != 'nn':
                            negative_opi[word] += 1
                            if not positive_word_total[word]:
                                positive_word_total[word] = count_pos
                                negative_word_total[word] = count_neg
            else:
                if flag:
                    for target in candidate:
                        if candidate[target] != 'nn':
                            negative_opi[word] += 1
                            if positive_word_total[word]:
                                positive_word_total[word] -= 1
                                negative_word_total[word] += 1
                            else:
                                positive_word_total[word] = count_pos - 1
                                negative_word_total[word] = count_neg + 1
                else:
                    for target in candidate:
                        if candidate[target] != 'nn':
                            positive_opi[word] += 1
                            if positive_word_total[word]:
                                positive_word_total[word] += 1
                                negative_word_total[word] -= 1
                            else:
                                positive_word_total[word] = count_pos + 1
                                negative_word_total[word] = count_neg - 1                   
    postive_file.close()
    pos_parser.close()

for city in cityList:
    # Read in the positive file
    pos_parser_file = ParseResultAddress + city + '_positive_seg.out.parse_result_positive' + city + '.1000.stp'
    neg_parser_file = ParseResultAddress + city + '_negative_seg.out.parse_result_negative' + city + '.1000.stp'
    positive_file_name = city + '_positive_pos.out'
    pos_file_address = POSaddress + positive_file_name
    BuildingTheVocab(1, pos_parser_file, pos_file_address)

    # Read in the negative file
    negative_file_name = city + '_negative_pos.out'
    # negative_file = open(POSaddress + negative_file_name, 'r', encoding = 'utf-8')
    pos_file_address = POSaddress + negative_file_name
    BuildingTheVocab(0, neg_parser_file, pos_file_address)
    # for lines in negative_file:
    #     lines = lines[:-1]
    #     bagOfWords = lines.split()
    #     wordbags = {}
    #     relationTemp = {}
    #     for words in bagOfWords:
    #         if words.split('#')[1] == 'VA' or words.split('#')[1] == 'JJ' or words.split('#')[1] == 'AD':
    #             wordbags[words.split('#')[0]] = 1
    #     lines = neg_parser.readline()
    #     line = lines[:-1]
    #     while line:
    #         relationTemp.setdefault(line.split()[1].split('-')[0], {})[line.split('(')[1].split('-')[0]] = 1
    #         relationTemp.setdefault(line.split('(')[1].split('-')[0],{})[line.split()[1].split('-')[0]] = 1
    #         lines = neg_parser.readline()
    #         line = lines[:-1]
    #     for word in wordbags:
    #         half_flag = 0
    #         if word not in relationTemp:
    #             half_flag = 1
    #             word_2 = strB2Q(word)
    #             if word_2 not in relationTemp:
    #                 print(word_2)
    #                 continue
    #             else:
    #                 word = word_2
    #         tempList = relationTemp[word]
    #         if half_flag:
    #             word = strQ2B(word)
    #             half_flag = 0
    #         for everyAttach in tempList:
    #             # everyAttach is the linkage in Dependency Parser
    #             if everyAttach in neg:

    #             else:
                    
    # negative_file.close()
    # neg_parser.close()

# Convert counting to the nagetive

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
    Total_word_list[words] = 1
    if words in negative_opi:
        word_frequency = positive_opi[words] + negative_opi[words]
        left = log2((N * positive_opi[words]) / (positive_word_total[words] * word_frequency))
        right = (negative_word_total[words] - negative_opi[words]) * log2((N * (negative_word_total[words] - negative_opi[words])) / (negative_word_total[words] * (N - negative_opi[words] - positive_opi[words]))) / N
        counter_st_1[words] = round((left + right), 4)
        counter_st_2[words] = round((positive_opi[words] / positive_word_total[words]) / (negative_opi[words] / negative_word_total[words]), 4)
        counter_st_3[words] = round((positive_opi[words]) / word_frequency, 4)
    else:
        pure_positive[words] = positive_opi[words]
        # print('Absolute positive word!!',words)

# Method 1,2,3(negative)
for words in negative_opi:
    Total_word_list[words] = 1
    if words in positive_opi:
        word_frequency = positive_opi[words] + negative_opi[words]
        left = log2((N * negative_opi[words]) / (negative_word_total[words] * word_frequency))
        right = (positive_word_total[words] - positive_opi[words]) * log2((N * (positive_word_total[words] - positive_opi[words])) / (positive_word_total[words] * (N - negative_opi[words] - positive_opi[words]))) / N
        neg_counter_st_1[words] = round((left + right), 4)
        # neg_counter_st_1[words] = round(negative_opi[words] * (log2(negative_opi[words] / ((negative_word_total[words] * (positive_opi[words] + negative_opi[words])) / (count_pos + count_neg)))), 4)
        neg_counter_st_2[words] = round((negative_opi[words] / negative_word_total[words]) / (positive_opi[words] / positive_word_total[words]), 4)
        neg_counter_st_3[words] = round((negative_opi[words]) / word_frequency, 4)
    else:
        pure_nagetive[words] = negative_opi[words]
        # print('Absolute negative word!!',words)

# Method 4(Chi-square)
for words in Total_word_list:
    N_11 = positive_opi[words]
    N_10 = negative_opi[words]
    N_01 = positive_word_total[words] - positive_opi[words]
    N_00 = negative_word_total[words] - negative_opi[words]
    E_11 = (N_11 + N_10) * (N_11 + N_01) / N
    E_10 = (N_11 + N_10) * (N_10 + N_00) / N
    E_01 = (N_11 + N_01) * (N_01 + N_00) / N
    E_00 = (N_01 + N_00) * (N_10 + N_00) / N
    counter_chi_square[words] = round(((pow((N_11 - E_11),2) / E_11) + (pow((N_00 - E_00),2) / E_00)), 4)
    neg_counter_chi_square[words] = round(((pow((N_10 - E_10),2) / E_10) + (pow((N_01 - E_01),2) / E_01)), 4)
    

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
for element in chi_square_result:
    pos_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
pos_chi_square.close()

chi_square_result = neg_counter_chi_square.most_common()
for element in chi_square_result:
    neg_chi_square.write(element[0] + ' ' + str(element[1]) + '\n')
neg_chi_square.close()

# negator  词典的建立。。。。
# 那个词里面本身有没有“没”或者“不”字

# print(pure_nagetive.most_common(10))
# print(pure_positive.most_common(10))
# print(neg_counter_st_1.most_common(10))
# print(counter_st_1.most_common(10))
# print(neg_counter_st_2.most_common(10))
# print(counter_st_2.most_common(10))
# print(neg_counter_st_3.most_common(10))
# print(counter_st_3.most_common(10))
