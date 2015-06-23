import sys
import itertools

def counting(fp, fp2):
        total = 0
        global threshold
        for lines in fp:
                line = lines[:-1]
                sentence = line.split(' ', 1)[1]
                documentLabel = line.split('@@@@', 1)[0]
                bags = sentence.split()
                iCount = 0
                flag = 1
                for element in bags:
                        if element.rsplit('#', 1)[1] != 'PU':
                                iCount += 1
                        if iCount >= threshold:
                                total += 1
                                flag = 0
                                break
                if flag:
                        pass
                        # print(line)
                else:
                        # fp2.write(line[1:] + '\n')
                        fp2.write(documentLabel + '\n')
        print("Total {} clauses above threshold {}".format(total, threshold))

threshold = 4
def compare_lexicon(argv): 
        global threshold
        address = './Entry_processed/Context_Extracted'
        # lexicon_set = ['automatic', 'manual_corrected']
        lexicon_set = ['automatic']
        # fileAddress = [('naive', 'rule-based'), ('discourse', 'discourse')]
        fileAddress = [('discourse', 'discourse')]
        polarSet = ['positive', 'negative']
        # Context_discourse_negative_automatic_training.txt
        combinations = itertools.product(lexicon_set, fileAddress, polarSet)
        # outputName = './Entry_processed/Context_testing/ToBeLabeling_{}Above.txt'.format(threshold)
        outputName = './Entry_processed/Context_testing/DocumentLabeling_{}Above.txt'.format(threshold)
        # outputName = './Entry_processed/Context_testing/ToBeLabeling_TempAbove.txt'
        with open(outputName, 'w', encoding = 'utf-8') as fp2:
                for element in combinations:
                        fileName = '{}/{}/Context_{}_{}_{}_testing.txt'.format(address, element[1][1], element[1][0], element[2], element[0])
                        print("Case {} {} {}".format(element[1][0], element[2], element[0]))
                        with open(fileName, 'r', encoding = 'utf-8') as fp:
                                counting(fp, fp2)

if __name__ == '__main__':
        compare_lexicon(sys.argv[1:])