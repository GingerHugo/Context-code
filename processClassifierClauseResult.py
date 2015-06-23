# convert from inverted_index to doc features
import argparse
from collections import defaultdict
from collections import Counter
import sys, re
from commonDiscourseMarker import *
from commonIO import *
from commonVecTransform import *
from processTextDataCheck import *
import math
from random import randint
import itertools

def process_commands():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('-feature', action='store', default='TF-IDF')
        return parser.parse_args()

def EvaluateSVM(testPath, fileName, groundtruth):
        Correct = Counter()
        Total = Counter()
        with open (testPath + fileName, 'r', encoding = 'utf-8') as fp:
                count = 0
                for lines in fp:
                        if count not in groundtruth:
                                count += 1
                                continue
                        else:
                                result = int(lines[:-1])
                                if (result == groundtruth[count] % 2) and (groundtruth[count] != 5):
                                        Correct[groundtruth[count]] += 1
                                Total[groundtruth[count]] += 1
                                count += 1
        accuracy1 = round(float(Correct[1] + Correct[2]) / float(Total[1] + Total[2]), 4)
        accuracy2 = round(float(Correct[3] + Correct[4]) / float(Total[3] + Total[4]), 4)
        accuracy3 = round(float(Correct[1] + Correct[2] + Correct[3] + Correct[4]) / float(Total[1] + Total[2] + Total[3] + Total[4]), 4)
        print('{} cases...'.format(fileName))
        print('Trivial case accuracy {}, with {}/{}'.format(accuracy1, (Correct[1] + Correct[2]), (Total[1] + Total[2])))
        print('Complicated case accuracy {}, with {}/{}'.format(accuracy2, (Correct[3] + Correct[4]), (Total[3] + Total[4])))
        print('Total case accuracy {}, with {}/{}'.format(accuracy3, (Correct[1] + Correct[2] + Correct[3] + Correct[4]), (Total[1] + Total[2] + Total[3] + Total[4])))

def ProcessingSVMResult(method_set, lexicon_set, groundtruth, path, feature):
        testPath = '{}/Context_Test_Result/BOW_clause/'.format(path)
        file1 = '{}_Context_Whole_entry_testing_clause_Result.txt'.format(feature)
        file2 = '{}_Raw_Whole_entry_testing_clause_Result.txt'.format(feature)
        EvaluateSVM(testPath, file1, groundtruth)
        EvaluateSVM(testPath, file2, groundtruth)
        combinations = itertools.product(method_set, lexicon_set)
        for tuples in combinations:
                fileName = '{}_{}_{}_clause_testResult.txt'.format(feature, tuples[0], tuples[1])
                EvaluateSVM(testPath, fileName, groundtruth)

def EvaluateCNN(testPath, fileName, groundtruth):
        Correct = Counter()
        Total = Counter()
        positiveUpper = 12802
        with open (testPath + fileName, 'r', encoding = 'utf-8') as fp:
                count = 0
                for lines in fp:
                        if count not in groundtruth:
                                count += 1
                                continue
                        else:
                                result = int(lines[:-1])
                                if count < positiveUpper:
                                        result = result ^ 1
                                else:
                                        result = result ^ 0
                                if (result == groundtruth[count] % 2) and (groundtruth[count] != 5):
                                        Correct[groundtruth[count]] += 1
                                Total[groundtruth[count]] += 1
                                count += 1
        # print(Total)
        # print(count)
        accuracy1 = round(float(Correct[1] + Correct[2]) / float(Total[1] + Total[2]), 4)
        accuracy2 = round(float(Correct[3] + Correct[4]) / float(Total[3] + Total[4]), 4)
        accuracy3 = round(float(Correct[1] + Correct[2] + Correct[3] + Correct[4]) / float(Total[1] + Total[2] + Total[3] + Total[4]), 4)
        print('{} cases...'.format(fileName))
        print('Trivial case accuracy {}, with {}/{}'.format(accuracy1, (Correct[1] + Correct[2]), (Total[1] + Total[2])))
        print('Complicated case accuracy {}, with {}/{}'.format(accuracy2, (Correct[3] + Correct[4]), (Total[3] + Total[4])))
        print('Total case accuracy {}, with {}/{}'.format(accuracy3, (Correct[1] + Correct[2] + Correct[3] + Correct[4]), (Total[1] + Total[2] + Total[3] + Total[4])))

def ProcessingCNNResult(method_set, lexicon_set, groundtruth, path, feature):
        testPath = '{}/Context_Test_Result/CNN_clause/'.format(path)
        file1 = '{}_Feature_Context_Whole_entry_testing_5epochs_Result.txt'.format(feature)
        file2 = '{}_Feature_Raw_Whole_entry_testing_5epochs_Result.txt'.format(feature)
        EvaluateCNN(testPath, file1, groundtruth)
        EvaluateCNN(testPath, file2, groundtruth)
        combinations = itertools.product(method_set, lexicon_set)
        for tuples in combinations:
                fileName = '{}_Feature_{}_{}_testing_5epochs_Result.txt'.format(feature, tuples[0], tuples[1])
                EvaluateCNN(testPath, fileName, groundtruth)     

def ReadInGroundtruth(groundtruth, path):
        upper_limit = 10483
        fileName = '{}/Context_testing/ToBeLabeling_4Above.txt'.format(path)
        referFile = '{}/Context_testing/ToBeLabeling_0Above.txt'.format(path)
        with open(referFile, 'r', encoding = 'utf-8') as fp:
                with open(fileName, 'r', encoding = 'utf-8') as fp2:
                        count = 0
                        for lines in fp2:
                                candidate = lines[:-1].split('@@@@', 1)
                                referLine = fp.readline()[:-1]
                                while (referLine.split('@@@@', 1)[1] != candidate[1]):
                                        count += 1
                                        referLine = fp.readline()[:-1]
                                if candidate[0]:
                                        groundtruth[count] = int(candidate[0])
                                count += 1
        if len(groundtruth) != upper_limit:
                # print("ReadInGroundtruth error!! Lexicon length error!!!")
                # print(len(groundtruth))
                print(count)

def processClassifierClauseResult(args):
        path = './Entry_processed'
        groundtruth = defaultdict(int)
        ReadInGroundtruth(groundtruth, path)
        # print(groundtruth)
        lexicon_set = ['automatic', 'manual']
        method_set = ['naive', 'discourse']
        if args.feature == 'Glove' or args.feature == 'word2vec':
                lexicon_set = ['automatic', 'manual_corrected']
                ProcessingCNNResult(method_set, lexicon_set, groundtruth, path, args.feature)
        else:
                ProcessingSVMResult(method_set, lexicon_set, groundtruth, path, args.feature)

if __name__=="__main__":
        args = process_commands()
        processClassifierClauseResult(args)