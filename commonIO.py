from math import *
import sys
from collections import *

def Calculation(package, threshold, EntryCount, WordCount, IPTotalNumber):
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
        N = IPTotalNumber['positive'] + IPTotalNumber['negative']
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
                        left = positiveCase * log2((N * positiveCase) / (EntryCount[word]['positive'] * word_frequency))
                        right = negativeCase * log2((N * negativeCase) / (EntryCount[word]['negative'] * word_frequency))
                        counter_st_1[word] = round(left, 4)
                        counter_st_2[word] = round((positiveCase / EntryCount[word]['positive']) / (negativeCase / EntryCount[word]['negative']), 4)
                        counter_st_3[word] = round(positiveCase / word_frequency, 4)
                        neg_counter_st_1[word] = round(right, 4)
                        neg_counter_st_2[word] = round((negativeCase / EntryCount[word]['negative']) / (positiveCase / EntryCount[word]['positive']), 4)
                        neg_counter_st_3[word] = round(negativeCase / word_frequency, 4)
                else:
                        if positiveCase:
                                pure_positive[word] = WordCount[word]['positive']
                        else:
                                pure_nagetive[word] = WordCount[word]['negative']
                N_11 = positiveCase
                N_10 = negativeCase
                N_01 = EntryCount[word]['positive'] - positiveCase
                N_00 = EntryCount[word]['negative'] - negativeCase
                counter_chi_square[word] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)
                neg_counter_chi_square[word] = round((pow((N_11 * N_00 - N_10 * N_01), 2) * (N_11 + N_10 + N_01 + N_00) / ((N_11 + N_10) * (N_11 + N_01) * (N_00 + N_01) * (N_00 + N_10))), 4)
        total = (counter_st_1, counter_st_2, counter_st_3, counter_chi_square, neg_counter_st_1, neg_counter_st_2, neg_counter_st_3, neg_counter_chi_square, pure_positive, pure_nagetive)
        for x in range(0, len(total)):
                package.append(total[x])

def OutputResult(package, methodType):
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

        # Vocaddress = './experiment/Entry_processed/lexicon_build/'
        if methodType == 'naive':
                Vocaddress = './Entry_processed/lexicon_build/rule-based/'
        else:
                Vocaddress = './Entry_processed/lexicon_build/discourse/'
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
