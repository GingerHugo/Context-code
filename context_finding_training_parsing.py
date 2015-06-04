import string  
import re  
import sys
import os
from collections import *
from math import *
from nltk.tree import *

def ReadInLexicon(Lexicon, fileName):
    fp = open(fileName , 'r', encoding = 'utf-8')
    for lines in fp:
        word = lines[:-1].split()[0]
        Lexicon[word] = 1
    fp.close()

def ContextFiltering(Lexicon, Input, OutputT, OutputC, Input2):
    NotationSet = {'，',','}
    LexiconSet = set(Lexicon.keys())
    p = re.compile( '(，|,|\n)')
    with open(Input, 'r', encoding = 'utf-8') as fp:
        with open(OutputT, 'w', encoding = 'utf-8') as fpContext:
            with open(OutputC, 'w', encoding = 'utf-8') as fpComment:
                with open(Input2, 'r', encoding = 'utf-8') as fp
                for lines in fp:
                    ClauseSet = {'IP','CP'}
                    line = lines[:-1]
                    if line.startswith('(ROOT'):
                        tree = Tree.fromstring(line)
                        ptree = ParentedTree.convert(tree)
                        if len(ptree) != 1:
                            print("unnormal")


                # for lines in fp:
                #     line = lines[:-1]
                #     segments = re.split('，|,', lines)
                #     context = []
                #     for eachSeg in segments:
                #         eachSeg
                #         tree2 = Tree.fromstring('(S (NP I) (VP (V enjoyed) (NP my cookie)))')



                #         BagOfWords = set(eachSeg.split())
                #         if BagOfWords & LexiconSet:
                #             fpComment.write(p.sub('',eachSeg) + '\n')
                #         else:
                #             context.append(eachSeg)
                #     if context:
                #         fpContext.write(p.sub('',context[0]))
                #         for x in range(1,len(context)):
                #             fpContext.write(p.sub('',context[x]))
                #         fpContext.write('\n')

def ContextFinding(Lexicon, polar):
    Address = 'G:/booking.com/FullParsingResult/'
    Address_lex = 'G:/booking.com/training/'
    filePrefix = 'FullPasingResult_segmented_' + polar + '_'
    filePrefix2 = 'segmented_' + polar + '_'
    outTprefix = 'context_' + polar + '_'
    outCprefix = 'comment_' + polar + '_'
    FileSet = {'training.txt', 'testing.txt'}
    for eachSet in FileSet:
        Input = Address + filePrefix + eachSet
        Input2 = Address_lex + filePrefix2 + eachSet
        OutputT = Address + outTprefix + 'FullParsing_' + eachSet
        OutputC = Address + outCprefix + 'FullParsing_' + eachSet
        ContextFiltering(Lexicon, Input, OutputT, OutputC, Input2)

def FindingMain(argv):
    Lexicon = {}
    # Address = 'G:/booking.com/FullParsingResult'
    Address_lex = 'G:/booking.com/training/'
    polarizationSet = {'positive', 'negative'}
    for polar in polarizationSet:
        fileName = Address_lex + 'voc_final_' + polar + '_checked.txt'
        ReadInLexicon(Lexicon, fileName)
        ContextFinding(Lexicon, polar)





if __name__ == '__main__':
    FindingMain(sys.argv[1:])
