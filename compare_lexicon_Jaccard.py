import sys
import itertools

def GetDictinary(fp, candidateSet):
        for lines in fp:
                candidateSet.add(lines[:-1])

def compare_lexicon_element(lexiconList, element):
        naive_lexicon_set = lexiconList[0]
        discourse_lexicon_set = lexiconList[1]
        intersection = len(naive_lexicon_set & discourse_lexicon_set)
        union = len(naive_lexicon_set | discourse_lexicon_set)
        print("Case {} {}:".format(element[0], element[1][0]))
        print("Naive {} cases and discourse {} cases".format(len(naive_lexicon_set), len(discourse_lexicon_set)))
        print("with {} intersection and {} union".format(intersection, union))

def compare_lexicon(argv): 
        address = './Entry_processed/lexicon_build'
        polarizationSet = ['positive', 'negative']
        lexicon_set = [('automatic',''), ('manual_corrected', '_man_corrected')]
        fileAddress = [('rule-based', 'naive'), ('discourse', 'discourse')]
        combinations = itertools.product(polarizationSet, lexicon_set)
        for element in combinations:
                lexiconList = [set(), set()]
                for index_Count in range(0, 2):
                        fileName = '{}/{}/voc_{}_final_{}{}.txt'.format(address, fileAddress[index_Count][0], fileAddress[index_Count][1], element[0], element[1][1])
                        with open(fileName, 'r', encoding = 'utf-8') as fp:
                                GetDictinary(fp, lexiconList[index_Count])
                compare_lexicon_element(lexiconList, element)

if __name__ == '__main__':
        compare_lexicon(sys.argv[1:])