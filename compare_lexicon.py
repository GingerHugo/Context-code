import sys

def GetDictinary(fp, candidateSet):
        for lines in fp:
                candidateSet.add(lines[:-1])

def CheckPrecision(fileName, lexicon, deleteset, common_set):
        flag = 1
        count = 0
        total = 0
        bag = []
        outputname = fileName[:-4] + '_man_corrected.txt'
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                with open(outputname, 'w', encoding = 'utf-8') as fp2:
                        for lines in fp:
                                line = lines[:-1]
                                word = line.rsplit('-',1)[0]
                                tag = line.rsplit('-',1)[1]
                                if (word in lexicon) or (line in lexicon):
                                        if tag != 'NN' and tag != 'VC' :
                                                count += 1
                                                total += 1
                                                fp2.write(line + '\n')
                                                common_set.add(line)
                                elif (word in deleteset) or (line in deleteset):
                                        if tag != 'NN' and tag != 'VC':
                                                total += 1
                                else:
                                        flag = 0
                                        # print(word)
                                        # print(line)
                                        bag.append(line)
        if flag:
                precision = float(count) / float(total)
                print('Total {} words output'.format(total))
                print('Hit {} words'.format(count))
                print(fileName, precision)
        else:
                print(fileName)
                for element in bag:
                        print(element)

def ExtendVocabulary(lexicon, fp1, fp2):
        for lines in fp2:
                word = lines.split()[0]
                if word not in lexicon:
                        fp1.write(word + '\n')

def OutputLexicon(fp, common_set):
        for word in common_set:
                fp.write(word + '\n')

def compare_lexicon(argv): 
        address1 = './Entry_processed/lexicon_build/rule-based/'
        address2 = './Entry_processed/lexicon_build/discourse/'
        addressList = {}
        addressList['naive'] = address1
        addressList['discourse']  = address2
        address3 = './Entry_processed/lexicon_build/'
        positive_lexicon = set()
        negative_lexicon = set()
        positive_delete = set()
        negative_delete = set()
        with open(address3 + 'voc_final_positive_groundtruth.txt', 'r', encoding = 'utf-8') as fp:
                GetDictinary(fp, positive_lexicon)
        with open(address3 + 'voc_final_negative_groundtruth.txt', 'r', encoding = 'utf-8') as fp:
                GetDictinary(fp, negative_lexicon)
                # print(negative_lexicon)

        # with open(address3 + 'voc_final_positive_deleted.txt', 'w', encoding = 'utf-8') as fp1:
        #     with open(address1 + 'voc_final_positive.txt', 'r', encoding = 'utf-8') as fp2:
        #         ExtendVocabulary(positive_lexicon, fp1, fp2)
        # with open(address3 + 'voc_final_negative_deleted.txt', 'w', encoding = 'utf-8') as fp1:
        #     with open(address1 + 'voc_final_negative.txt', 'r', encoding = 'utf-8') as fp2:
        #         ExtendVocabulary(negative_delete, fp1, fp2)

        with open(address3 + 'voc_final_positive_deleted.txt', 'r', encoding = 'utf-8') as fp:
                GetDictinary(fp, positive_delete)
        with open(address3 + 'voc_final_negative_deleted.txt', 'r', encoding = 'utf-8') as fp:
                GetDictinary(fp, negative_delete)
        common_positive = set()
        common_negative = set()
        for label in addressList:
                CheckPrecision(addressList[label] + 'voc_' + label + '_final_negative.txt', negative_lexicon, negative_delete, common_negative)
                CheckPrecision(addressList[label] + 'voc_' + label + '_final_positive.txt', positive_lexicon, positive_delete, common_positive)
        with open(address3 + 'voc_union_positive.txt', 'w', encoding = 'utf-8') as fp:
                OutputLexicon(fp, common_positive)
        with open(address3 + 'voc_union_negative.txt', 'w', encoding = 'utf-8') as fp:
                OutputLexicon(fp, common_negative)

if __name__ == '__main__':
        compare_lexicon(sys.argv[1:])