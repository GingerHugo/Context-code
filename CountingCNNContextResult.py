import sys
import itertools

def counting(fp, element):
        total = 0
        error = 0
        for lines in fp:
                line = int(lines[:-1])
                if line:
                        error += 1
                total += 1
        correct = total - error
        Accuracy = round(float(correct) / float(total), 4)
        print("Case {} {} {}".format(element[0], element[1], element[2]))
        print("Accuracy is {}, with {} correct cases and {} in total".format(Accuracy, correct, total))

def compare_lexicon(argv): 
        address = './Entry_processed/Context_Test_Result/CNN'
        featureSet = ['Glove_Feature', 'word2vec_Feature']
        lexicon_set = ['automatic', 'manual_corrected']
        fileAddress = ['naive', 'discourse']
        posfix = '_testing_5epochs_Result.txt'
        combinations = itertools.product(featureSet, lexicon_set, fileAddress)
        for element in combinations:
                fileName = '{}/{}_{}_{}{}'.format(address, element[0], element[2], element[1], posfix)
                with open(fileName, 'r', encoding = 'utf-8') as fp:
                        counting(fp, element)

if __name__ == '__main__':
        compare_lexicon(sys.argv[1:])