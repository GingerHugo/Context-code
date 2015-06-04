# convert from inverted_index to doc features
import argparse
from collections import defaultdict
import sys, re
from commonDiscourseMarker import *
from commonIO import *
from commonVecTransform import *
from processTextDataCheck import *
import math
from random import randint

def process_commands():
        parser = argparse.ArgumentParser(description=__doc__)
        # parser.add_argument('file_path')
        # parser.add_argument('voc_path')
        parser.add_argument('-feature', action='store', default='TF-IDF')
        # parser.add_argument('-output', action='store_true', default=False)
        # parser.add_argument('-feature', action='store_true', default=False)
        return parser.parse_args()

def GetLabel(polar):
        if polar == 'positive':
                return 1
        else:
                return 0

negator_set = set()

def ProcessingContextFile(Context_file, context_Result, polar, fp, CNNFlag = False):
        FileLabel = GetLabel(polar)
        with open(Context_file, 'r', encoding = 'utf-8') as fp2:
                for lines in fp2:
                        if CNNFlag:
                                result = (FileLabel^int(fp.readline()[:-1]))
                        else:
                                result = int(fp.readline()[:-1])
                        line = lines[:-1]
                        label = line.split(' ', 1)[0]
                        tagBags = label.split('@@@@')
                        ReverseFlag = 0
                        if tagBags[0] == 'P':
                                if FileLabel != 1:
                                        ReverseFlag = 1
                                index = 1
                        else:
                                if FileLabel != 0:
                                        ReverseFlag = 1
                                index = 0
                        if (not context_Result[index].get(int(tagBags[1]), 0)) or (not context_Result[index][int(tagBags[1])].get(int(tagBags[2]), 0)):
                                context_Result[index][int(tagBags[1])][int(tagBags[2])] = (2 * ((ReverseFlag)^result) - 1)
                        else:
                                # print("Duplicate case!!!")
                                previous = context_Result[index][int(tagBags[1])][int(tagBags[2])]
                                context_Result[index][int(tagBags[1])][int(tagBags[2])] = (2 * ((ReverseFlag)^result) - 1) + previous
                                # print("Duplicate case!!! {}".format((2 * ((ReverseFlag)^result) - 1) + previous))
        return context_Result

def ProcessingCommentFile(comment_file, comment_Result, polar, DP_Result, LexiconPositive, LexiconNegative, Line_Init):
        global negator_set
        FileLabel = GetLabel(polar)
        with open(comment_file, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        label = line.split(' ', 1)[0]
                        sentence = line.split(' ', 1)[1]
                        tagBags = label.split('@@@@')
                        # print(tagBags)
                        ReverseFlag = 0
                        if tagBags[0] == 'P':
                                index = 1
                                if FileLabel != 1:
                                        ReverseFlag = 1
                        else:
                                index = 0
                                if FileLabel != 0:
                                        ReverseFlag = 1
                        sentenceInit = int(tagBags[3])
                        Line_Number = int(tagBags[1])
                        Line_Init_number = Line_Init[index]
                        DP_Result_line = DP_Result[index][Line_Number - Line_Init_number]
                        DPResultDict = defaultdict(dict)
                        # print(DP_Result_line)
                        # print("here")
                        # print(Line_Number - Line_Init_number)
                        ParseTheDPResult(DPResultDict, DP_Result_line)
                        x = 0
                        voting = 0 
                        for words in sentence.split():
                                words = '{}-{}'.format(words.rsplit('#', 1)[0], words.rsplit('#', 1)[1])
                                if (words not in LexiconPositive) and (words not in LexiconNegative):
                                        x += 1
                                        continue
                                else:
                                        if words in LexiconPositive:
                                                result = 1
                                        else:
                                                result = 0
                                        word = words.rsplit('#', 1)[0]
                                        Negatorflag = CheckNegatorFromDP(word, (sentenceInit + x), DPResultDict, negator_set)
                                        x += 1
                                        if ((Negatorflag)^result):
                                                voting += 1
                                        else:
                                                voting -= 1
                        if voting > 0:
                                FlagTemp = ((ReverseFlag)^1)
                        elif voting < 0:
                                FlagTemp = ((ReverseFlag)^0)
                        else:
                                FlagTemp = ((ReverseFlag)^randint(0,1))
                        # FlagTemp = FileLabel^ReverseFlag 
                        if (not comment_Result[index].get(int(tagBags[1]), 0)) or (not comment_Result[index][int(tagBags[1])].get(int(tagBags[2]), 0)):
                                comment_Result[index][int(tagBags[1])][int(tagBags[2])] = (2 * FlagTemp - 1)
                        else:
                                 previous = comment_Result[index][int(tagBags[1])][int(tagBags[2])]
                                 comment_Result[index][int(tagBags[1])][int(tagBags[2])] = (2 * FlagTemp - 1) + previous
        return comment_Result

def ProcessingSVMResult(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result, featureType):
        context_Result = [defaultdict(dict), defaultdict(dict)]
        ContextOutputAddress = './Entry_processed/Context_Extracted'
        ResultOutputAddress = './Entry_processed/Context_Test_Result'

        # Context Processing Part
        print("Context Processing Part")
        ResultFile = '{}/{}/{}_{}_{}testResult.txt'.format(ResultOutputAddress, methodType[0], featureType, methodType[1], lexiconType)
        with open(ResultFile, 'r', encoding = 'utf-8') as fp:
                for polar in polarSet:
                        Context_file = '{}/{}/Context_{}_{}_{}testing.txt'.format(ContextOutputAddress, methodType[0], methodType[1], polar, lexiconType)
                        context_Result = ProcessingContextFile(Context_file, context_Result, polar, fp, False)
        ProcessingCommon(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result, context_Result)

def ProcessingCNNResult(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result):
        context_Result = [defaultdict(dict), defaultdict(dict)]
        ContextOutputAddress = './Entry_processed/Context_Extracted'
        ResultOutputAddress = './Entry_processed/Context_Test_Result/CNN'        

        # Context Processing Part
        print("Context Processing Part")
        TestingDataFile = '{}/{}_{}testing.txt'.format(ResultOutputAddress, methodType[1], lexiconType)
        with open (TestingDataFile, 'r', encoding = 'utf-8') as fp:
                if int(fp.readline()[:-1].rsplit(' ', 1)[1]) == 1:
                        polarSet = ['positive', 'negative']
                else:
                        polarSet = ['negative', 'positive']
        ResultFile = '{}/{}_{}testing_25epochs_Result.txt'.format(ResultOutputAddress, methodType[1], lexiconType)
        with open(ResultFile, 'r', encoding = 'utf-8') as fp:
                for polar in polarSet:
                        Context_file = '{}/{}/Context_{}_{}_{}testing.txt'.format(ContextOutputAddress, methodType[0], methodType[1], polar, lexiconType)
                        context_Result = ProcessingContextFile(Context_file, context_Result, polar, fp, True)
        # print(len(context_Result[0]))
        # # print(context_Result[0])
        # print(len(context_Result[1]))
        ProcessingCommon(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result, context_Result)

def ProcessingCommon(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result, context_Result):
        global negator_set
        polarSet = ['positive', 'negative']
        CommentOutputAddress = './Entry_processed/Comment_Extracted'
        TestingDataAddress = './Entry_processed/Entry_segmented'
        comment_Result = [defaultdict(dict), defaultdict(dict)]

        # Comment Processing Part
        print("Comment Processing Part")
        Line_Init = LineInit_List
        for polar in polarSet:
                comment_file = '{}/{}/Comment_{}_{}_{}testing.txt'.format(CommentOutputAddress, methodType[0], methodType[1], polar, lexiconType)
                comment_Result = ProcessingCommentFile(comment_file, comment_Result, polar, DP_Result, LexiconPositive, LexiconNegative, Line_Init)
        # print(len(comment_Result[0]))
        # print(comment_Result[0])
        # print(len(comment_Result[1]))

        # Predict Testing Entry
        total = 0
        hit = 0
        total_comment_entry = 0
        hit_comment_entry = 0
        BlackListAddress = './Entry_processed/DeleteList'
        for polar in polarSet:
                TestFile = '{}/Segmented_Entry_{}_testing.txt'.format(TestingDataAddress, polar)
                print("Output the test result of method {}_{}, in Segmented_Entry_{}_testing.txt file".format(methodType[1], lexiconType[:-1], polar))
                label = GetLabel(polar)
                Init = Line_Init[label]
                # print(Init)
                hitTemp = 0
                totalTemp = 0
                BlackListName = '{}/Entry_{}_testing.txt'.format(BlackListAddress, polar)
                BlackList = set()
                ReadInBlackList(BlackList, BlackListName)
                with open(TestFile, 'r', encoding = "utf-8") as fp:
                        count = 0
                        for lines in fp:
                                commentEntryFlag = 0
                                Line_Number = count + Init
                                contextPart = context_Result[label].get(Line_Number, 0)
                                commentPart = comment_Result[label].get(Line_Number, 0)
                                VotingList = []
                                if commentPart:
                                        VotingList.append(commentPart)
                                        commentEntryFlag = 1
                                if contextPart:
                                        VotingList.append(contextPart)
                                        commentEntryFlag = 0
                                maxi_fragment = 0
                                if not len(VotingList):
                                        if  Line_Number not in BlackList:
                                                print("DeleteList case!!")
                                                print(Line_Number)
                                                print(label)
                                        count += 1
                                        continue
                                for element in VotingList:
                                        for index in element:
                                                if index > maxi_fragment:
                                                        maxi_fragment = index
                                voting_entry = 0
                                for iCount in range(0, maxi_fragment + 1):
                                        voting_temp = 0
                                        flagJudge = 1
                                        for element in VotingList:
                                                if iCount in element:
                                                        flagJudge = 0
                                                        if element[iCount] > 0:
                                                                voting_temp += 1
                                                        elif element[iCount] < 0:
                                                                voting_temp -= 1
                                        if flagJudge:
                                                print("Illegal case, entry has no context and no comment in this number, too strange to be true!!!")
                                                print(Line_Number)
                                        if voting_temp > 0:
                                                voting_entry += 1
                                        elif voting_temp < 0:
                                                voting_entry -= 1
                                if voting_entry > 0:
                                        entryLabelPredict = 1
                                elif voting_entry < 0:
                                        entryLabelPredict = 0
                                else:
                                        entryLabelPredict = randint(0,1)
                                count += 1
                                totalTemp += 1
                                if commentEntryFlag:
                                        total_comment_entry += 1
                                if entryLabelPredict == label:
                                        hitTemp += 1
                                        if commentEntryFlag:
                                                hit_comment_entry += 1
                hit += hitTemp
                total += totalTemp
        accuracy = round(float(hit) / float(total), 4)
        print("Accuracy of Method {}_{} is {}, with {}/{}".format(methodType[1], lexiconType[:-1], accuracy, hit, total))
        accuracy_lexicon = round(float(hit_comment_entry) / float(total_comment_entry), 4)
        print("Accuracy of Lexicon built by Method {}_{} is {}, with {}/{}".format(methodType[1], lexiconType[:-1], accuracy_lexicon, hit_comment_entry, total_comment_entry))

def ReadInPasringResult(DP_file, DP_Result, polar):
        Label = GetLabel(polar)
        count = 0
        with open(DP_file, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        DP_Result[Label][count] = line
                        count += 1

def processClassifierResult(args):
        global negator_set
        # comment_Result = defaultdict(dict)
        # context_Result = defaultdict(dict)
        path = './Entry_processed/negator.txt'
        ReadInNegator(negator_set, path)
        ParseResultAddress = './Entry_processed/DP_Result'
        VocabularyAddress = './Entry_processed/lexicon_build'
        BlackListAddress = './Entry_processed/DeleteList'
        polarizationSet = ['positive', 'negative']
        lexicon_set = {'automatic_', 'manual_corrected_'}
        fileAddress = {('rule-based', 'naive'), ('discourse', 'discourse')}

        # Read in Dependency Result
        DP_Result = defaultdict(dict)
        for polar in polarSet:
                DP_file = '{}/DPResult_Segmented_Entry_{}_testing.txt'.format(ParseResultAddress, polar)
                ReadInPasringResult(DP_file, DP_Result, polar)

        # discourse line number bug fixing, next time this bug will not exist, so this segment is needed to changed!!! 
        Minimun_Line_Init = [defaultdict(dict), defaultdict(dict)]
        Minimun_Line_Init[0]['discourse']['automatic_'] = 0
        Minimun_Line_Init[1]['discourse']['automatic_'] = 0
        Minimun_Line_Init[0]['discourse']['manual_corrected_'] = 0
        Minimun_Line_Init[1]['discourse']['manual_corrected_'] = 0
        Minimun_Line_Init[0]['naive']['automatic_'] = 0
        Minimun_Line_Init[0]['naive']['manual_corrected_'] = 0
        Minimun_Line_Init[1]['naive']['automatic_'] = 0
        Minimun_Line_Init[1]['naive']['manual_corrected_'] = 0
        print("{} cases".format(args.feature))
        for methodType in fileAddress:
                # Read in lexicon
                for lexiconType in lexicon_set:
                        LexiconPositive = set()
                        LexiconNegative = set()
                        if lexiconType == 'automatic_':
                                fileName = '{}/{}/voc_{}_final_positive.txt'.format(VocabularyAddress, methodType[0], methodType[1])
                                ReadInLexicon(LexiconPositive, fileName)
                                fileName = '{}/{}/voc_{}_final_negative.txt'.format(VocabularyAddress, methodType[0], methodType[1])
                                ReadInLexicon(LexiconNegative, fileName)
                        else:
                                fileName = '{}/{}/voc_{}_final_positive_man_corrected.txt'.format(VocabularyAddress, methodType[0], methodType[1])
                                ReadInLexicon(LexiconPositive, fileName)
                                fileName = '{}/{}/voc_{}_final_negative_man_corrected.txt'.format(VocabularyAddress, methodType[0], methodType[1])
                                ReadInLexicon(LexiconNegative, fileName)
                        intersection = LexiconNegative & LexiconPositive
                        if intersection:
                                print("Lexicon not mutually exclusive!!!")
                                print(intersection)
                        LineInit_List = [Minimun_Line_Init[0][methodType[1]][lexiconType], Minimun_Line_Init[1][methodType[1]][lexiconType]]
                        if args.feature == 'CNN':
                                ProcessingCNNResult(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result)
                        else:
                                ProcessingSVMResult(methodType, lexiconType, LexiconPositive, LexiconNegative, LineInit_List, DP_Result, args.feature)

if __name__=="__main__":
        args = process_commands()
        processClassifierResult(args)        