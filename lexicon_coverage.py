import string  
import re  
import sys
import os
from collections import *
from math import *

def ReadInLexicon(Lexicon, fileName):
    fp = open(fileName , 'r', encoding = 'utf-8')
    for lines in fp:
        word = lines[:-1].split()[0]
        Lexicon[word] = 1
    fp.close()

def ContextFiltering(Lexicon, Input, OutputT, OutputC, numberSet):
    NotationSet = {'，',','}
    LexiconSet = set(Lexicon.keys())
    p = re.compile( '(，|,|\n)')
    with open(Input, 'r', encoding = 'utf-8') as fp:
        with open(OutputT, 'w', encoding = 'utf-8') as fpContext:
            with open(OutputC, 'w', encoding = 'utf-8') as fpComment:
                for lines in fp:
                    flag = 0
                    line = lines[:-1]
                    segments = re.split('，|,', lines)
                    context = []
                    numberSet['clause'] += len(segments)
                    for eachSeg in segments:
                        BagOfWords = set(eachSeg.split())
                        if BagOfWords & LexiconSet:
                            flag = 1
                            fpComment.write(p.sub('',eachSeg) + '\n')
                        else:
                            context.append(eachSeg)
                    numberSet['hassenti'] += (len(segments) - len(context))
                    if context:
                        fpContext.write(p.sub('',context[0]))
                        for x in range(1,len(context)):
                            fpContext.write(p.sub('',context[x]))
                        fpContext.write('\n')
                    numberSet['Instance'] += flag

def ContextFinding(Lexicon, polar):
    Address = 'G:/booking.com/training/'
    filePrefix = 'segmented_' + polar + '_'
    outTprefix = 'context_' + polar + '_'
    outCprefix = 'comment_' + polar + '_'
    FileSet = {'training.txt', 'testing.txt'}
    for eachSet in FileSet:
        Input = Address + filePrefix + eachSet 
        OutputT = Address + outTprefix + eachSet
        OutputC = Address + outCprefix + eachSet
        numberSet = Counter()
        ContextFiltering(Lexicon, Input, OutputT, OutputC, numberSet)
        print (eachSet, polar, numberSet['Instance'], numberSet['clause'], numberSet['hassenti'])

def ContextFindingEntry(Lexicon):
    pass

def FindingMain(argv):
    Lexicon = {}
    Address = 'G:/booking.com/training/'
    polarizationSet = {'positive', 'negative'}
    for polar in polarizationSet:
        fileName = Address + 'voc_final_' + polar + '_checked.txt'
        # fileName2 = Address + 
        ReadInLexicon(Lexicon, fileName)
        ContextFindingEntry(Lexicon)
        ContextFinding(Lexicon, polar)

if __name__ == '__main__':
    FindingMain(sys.argv[1:])
