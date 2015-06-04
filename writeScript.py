import string  
import re  
import sys
import os
import itertools
from commonIO import *

def Counting(fileName, deleteFileName, SentenceLengh):
        global  Marker_set, negator_set
        count = 0
        over = 0
        count_DiscourseMarker = 0
        count_Negator = 0
        count_DiscourseMarkerDelete = 0
        count_NegatorDelete = 0
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                # with open(deleteFileName, 'w', encoding = 'utf-8') as fp2:
                for lines in fp:
                        bags = lines[:-1].split()
                        if set(bags) & Marker_set:
                                count_DiscourseMarker += 1
                                if len(bags) <= SentenceLengh:
                                        count_DiscourseMarkerDelete += 1
                        if set(bags) & negator_set:
                                count_Negator += 1
                                if len(bags) <= SentenceLengh:
                                        count_NegatorDelete += 1
                        if len(bags) > SentenceLengh:
                                # print(lines)
                                over += 1
                                # fp2.write("{}\n".format(count))
                        count += 1
        print(fileName)
        print("total {} entires with {} more than {} longer".format(count, over, SentenceLengh))
        print("total {} entires with {} contains discourse markers and {} after delete".format(count, count_DiscourseMarker, count_DiscourseMarkerDelete))
        print("total {} entires with {} contains negators and {} after delete".format(count, count_Negator, count_NegatorDelete))

negator_set = set()
Marker_set = set()

def StatisticalCounting(args):
        global  Marker_set, negator_set
        # Read negator
        path = './Entry_processed/negator.txt'
        ReadInNegator(negator_set, path)
        # Read discourse marker
        path = './Entry_processed/connectives.csv'
        ReadInReverseDiscourseMarker(Marker_set, path)
        # Read entry file
        path = './Entry_processed/Entry_segmented'
        polarSet = ['positive', 'negative']
        crossSet = ['training', 'testing']
        combinations = itertools.product(polarSet, crossSet)
        deletePath = './Entry_processed/DeleteList'
        SentenceLengh = 60
        for tuples in combinations:
                fileName = '{}/Segmented_Entry_{}_{}.txt'.format(path, tuples[0], tuples[1])
                deleteFileName = '{}/Entry_{}_{}.txt'.format(deletePath, tuples[0], tuples[1])
                Counting(fileName, deleteFileName, SentenceLengh)

if __name__ == '__main__':
        # args = process_commands()
        StatisticalCounting(sys.argv[1:]) 