import string  
import re  
import sys
import os
import itertools
from commonIO import *

def GetLabel(polar):
        if polar == 'positive':
                return 'P'
        else:
                return 'N'

def Counting(fileName, polar):
        label = GetLabel(polar)
        count_total = 0
        count_reverse = 0
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        count_total += 1
                        tags = lines[:-1].split(' ', 1)[0]
                        fileLabel = tags.split('@@@@', 1)[0]
                        if fileLabel != label:
                                count_reverse += 1
        print(fileName)
        print("total {} clauses with {} reverse".format(count_total, count_reverse))

negator_set = set()
Marker_set = set()

def ClauseStatisticalCounting(args):
        # Read entry file
        path = './Entry_processed'
        polarSet = ['positive', 'negative']
        crossSet = ['training', 'testing']
        fileAddress = [('rule-based', 'naive'), ('discourse', 'discourse')]
        TypeSet = ['automatic', 'manual_corrected']
        prefixSet = [('Context', 'Context_Extracted'), ('Comment', 'Comment_Extracted')]
        combinations = itertools.product(prefixSet, fileAddress, polarSet, TypeSet, crossSet)
        for tuples in combinations:
                polar = tuples[2]
                fileName = '{}/{}/{}/{}_{}_{}_{}_{}.txt'.format(path, tuples[0][1], tuples[1][0], tuples[0][0], tuples[1][1], tuples[2], tuples[3], tuples[4])
                Counting(fileName, polar)

if __name__ == '__main__':
        ClauseStatisticalCounting(sys.argv[1:]) 