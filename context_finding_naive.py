import string  
import re  
import sys
import os
from collections import *
from math import *
from commonIO import *

def ReadInLexicon(Lexicon, fileName):
        fp = open(fileName , 'r', encoding = 'utf-8')
        for lines in fp:
                word = lines[:-1]
                Lexicon.add(word)
        fp.close()

def ContextFiltering(Lexicon, Input, OutputT, OutputC):
        NotationSet = {'，',','}
        LexiconSet = set(Lexicon.keys())
        p = re.compile( '(，|,|\n)')
        with open(Input, 'r', encoding = 'utf-8') as fp:
                with open(OutputT, 'w', encoding = 'utf-8') as fpContext:
                        with open(OutputC, 'w', encoding = 'utf-8') as fpComment:
                                for lines in fp:
                                        line = lines[:-1]
                                        segments = re.split('，|,', lines)
                                        context = []
                                        for eachSeg in segments:
                                                BagOfWords = set(eachSeg.split())
                                                if BagOfWords & LexiconSet:
                                                        # print(p.sub('',eachSeg))
                                                        # print(eachSeg)
                                                        if eachSeg.strip():
                                                                fpComment.write(eachSeg.strip() + '\n')
                                                else:
                                                        context.append(eachSeg)
                                        if context:
                                                temp = ''.join(context)
                                                # print(temp)
                                                if temp.strip():
                                                        # print("here!")
                                                        fpContext.write(temp.strip() + '\n')
                                                # fpContext.write(p.sub('',context[0]))
                                                # for x in range(1,len(context)):
                                                #         fpContext.write(p.sub('',context[x]))
                                                # fpContext.write('\n')

def ContextFinding(posFile, polar, Lexicon, fp1, fp2, BlackList):
        if polar == 'positive':
                lineInit = 'P'
        else:
                lineInit = 'N'
        middleFix = '@@@@'  
        CurrentLine = 0
        with open(posFile, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        if CurrentLine in BlackList:
                                CurrentLine += 1
                                continue
                        line = lines[:-1]
                        POSline = ' ' + line
                        it = 0
                        clauses = re.split(r' [，|,|。|\.|！|\!|\?|？|；|;]#PU', POSline)
                        clauseNumber = 0
                        for each in clauses:
                                if each and each.strip() and each.strip().rstrip():
                                        temp = each.strip().rstrip()
                                        words = temp.split()
                                        contextFlag = 1
                                        for x in range(0, len(words)):
                                                try:
                                                        word = words[x].rsplit('#', 1)[0]
                                                        POS_tag = words[x].rsplit('#', 1)[1]
                                                except:
                                                        print(words[x])
                                                else:
                                                        pass
                                                wordPair = word + '-' + POS_tag
                                                if wordPair in Lexicon:
                                                        contextFlag = 0
                                                        break
                                        stringToWrite = lineInit + middleFix + str(CurrentLine) + middleFix + str(clauseNumber) + middleFix + str(it) + middleFix + ' ' +temp
                                        if contextFlag:
                                                fp1.write(stringToWrite + '\n')
                                        else:
                                                fp2.write(stringToWrite + '\n')
                                        it += len(words)
                                        clauseNumber += 1
                                it += 1
                        CurrentLine += 1

def FindingMain(argv):
        Lexicon = set()
        VocabularyAddress = './Entry_processed/lexicon_build/rule-based/'
        BlackListAddress = './Entry_processed/DeleteList/'
        polarizationSet = {'positive', 'negative'}
        extracting_set = {'training', 'testing'}
        lexicon_set = {'automatic_', 'manual_corrected_'}
        ContextOutputAddress = './Entry_processed/Context_Extracted/rule-based/'
        CommentOutputAddress = './Entry_processed/Comment_Extracted/rule-based/'
        POSAddress = './Entry_processed/POSTagged/'
        for lexiconType in lexicon_set:
                if lexiconType == 'automatic_':
                        fileName = VocabularyAddress + 'voc_naive_final_positive.txt'
                        ReadInLexicon(Lexicon, fileName)
                        fileName = VocabularyAddress + 'voc_naive_final_negative.txt'
                        ReadInLexicon(Lexicon, fileName)
                else:
                        fileName = VocabularyAddress + 'voc_naive_final_positive_man_corrected.txt'
                        ReadInLexicon(Lexicon, fileName)
                        fileName = VocabularyAddress + 'voc_naive_final_negative_man_corrected.txt'
                        ReadInLexicon(Lexicon, fileName)
                for polar in polarizationSet:
                        for postfix in extracting_set:
                                with open(ContextOutputAddress + 'Context_naive_' + polar + '_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp1:
                                        with open(CommentOutputAddress + 'Comment_naive_' + polar + '_' + lexiconType + postfix + '.txt', 'w', encoding = 'utf-8') as fp2:
                                                posFile = POSAddress + 'POSTagged_Entry_' + polar + '_' + postfix + '.txt'
                                                BlackList = set()
                                                BlackListName = '{}Entry_{}_{}.txt'.format(BlackListAddress, polar, postfix)
                                                ReadInBlackList(BlackList, BlackListName)
                                                ContextFinding(posFile, polar,Lexicon, fp1, fp2, BlackList)

if __name__ == '__main__':
        FindingMain(sys.argv[1:])
