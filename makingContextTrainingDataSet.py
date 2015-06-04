import sys
import random
from processTextData import *


def ReadInLexicon(Lexicon, fileName):
        with open(fileName , 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        word = lines[:-1]
                        Lexicon.add(word)

def ExtractTestDoc(fp1, fp2, fp3, lexicon, polar):
        global SentenceThreshold 
        count = 0
        hit = 0
        hit_all = 0
        for lines in fp1:
                line = fp3.readline()
                bags = line[:-1].split()
                count += 1
                flag = 1
                for element in bags:
                        if (element.rsplit('#', 1)[0] + '-' + element.rsplit('#', 1)[1]) in lexicon:
                              flag = 0
                              break  
                if flag and (len(bags) <= SentenceThreshold):
                        fp2.write(lines)
                        hit += 1
                if flag:
                        hit_all += 1
        print('Final Statistics {}, total: {}, hit_all: {} hit: {}'.format(polar, count, hit_all, hit))

def ExtractMain(argv):
        lexicon = set()
        LexiconFile = './Entry_processed/lexicon_build/'
        segFile = './Entry_processed/Entry_segmented/'
        posFile = './Entry_processed/POSTagged/'
        outputFile = './Entry_processed/Context_Extracted/'
        ReadInLexicon(lexicon, LexiconFile + 'voc_union_negative.txt')
        ReadInLexicon(lexicon, LexiconFile + 'voc_union_positive.txt')
        PolarizedSet = {'positive','negative'}
        for polar in PolarizedSet:
                file1 = segFile + 'Segmented_Entry_' + polar + '_training.txt'
                file3 = posFile + 'POSTagged_Entry_' + polar + '_training.txt'
                file2 = outputFile + 'Context_Entire_Doc' + '_' + polar + '_training.txt'
                with open(file1, 'r', encoding = 'utf-8') as fp1:
                        with open(file2, 'w', encoding = 'utf-8') as fp2:
                                with open(file3, 'r', encoding = 'utf-8') as fp3:
                                        ExtractTestDoc(fp1, fp2, fp3, lexicon, polar)

if __name__ == '__main__':
        ExtractMain(sys.argv[1:])