import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys

def MiningFromText(flag, pos_parser_file):
    # detector = DiscourseMarker.LinkageDetector('G:/booking.com/Entry_processed/connectives.csv')
    with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
        count_line = 0
        for lines in fp:
            count_line += 1
            # print(count_line)
            line = lines[:-1]
            # print(line)
            if not line.startswith('(ROOT'):
                continue
            try:
                ptree = ParentedTree.fromstring(line)
            except:
                print(count_line)
                sentence = line.replace('(PU )','(PU ）')
                sentence = sentence.replace('(PU (','(PU （')
                ptree = ParentedTree.fromstring(sentence)
            else:
                continue
            
           


def BuildingDiscourse(argv):
    polarization = {'positive','negative'}
    ParseResultAddress = 'G:/booking.com/Entry_processed/Entry_fullparsing/'
    # mutex = multiprocessing.RLock()       # mutex lock of multi-threading
    prefix = 'FullPasingResult_Segmented_Entry_'
    for polar in polarization:
        if polar == 'positive':
            # pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
            # MiningFromText(1, pos_parser_file)
            pos_parser_file = ParseResultAddress + prefix + polar + '_testing.txt'
            MiningFromText(1, pos_parser_file)
        else:               # Read in the negative file
            # pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
            # MiningFromText(0, pos_parser_file)
            pos_parser_file = ParseResultAddress + prefix + polar + '_testing.txt'
            MiningFromText(0, pos_parser_file)


if __name__ == '__main__':
    BuildingDiscourse(sys.argv[1:])