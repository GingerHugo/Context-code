import sys
from collections import Counter

def TraverseLexicon(fileName, Lexicon, polar):
        fp = open(fileName, 'r', encoding = 'utf-8')
        flag = 1
        title = 'Absolute ' + polar + ' word:'
        title2 = 'Non-absolute ' + polar + ' word:'
        for lines in fp:
                lines = lines[:-1]
                if flag and lines:
                        if lines[:len(title)] != title:
                                if lines[:len(title2)] == title2:
                                        flag = 0
                                        continue
                                Lexicon[lines.split()[0]] = float(10000000.0)
                                # print(lines.split()[0])
                elif lines:
                        if lines.split()[0] not in Lexicon:
                                Lexicon[lines.split()[0]] = float(lines.split()[1])
        fp.close()

def DecisionMaking(outputFile, MILexicon, ChLexicon, LgLexicon, RRLexicon):
        p_value_thresh = 0.001
        p_value_table = {0.5:0.455, 0.10:2.706, 0.05:3.841, 0.02:5.412, 0.01:6.635, 0.001:10.828}
        threshold_Chi = p_value_table[p_value_thresh]
        threshold_MI = 300.00
        threshold_Lg = 3
        threshold_RR = 0.75
        fp = open(outputFile, 'w', encoding = 'utf-8')
        result = ChLexicon.most_common()
        for word in result:
                # print(word[1])
                if word[0].split('-')[0] == '满意':
                        print("MI ", MILexicon[word[0]])
                        print("Chi ", ChLexicon[word[0]])
                        print("Log ", LgLexicon[word[0]])
                        print("RR ", RRLexicon[word[0]])
                if word[1] == 10000000.0:
                        # print(word[0])
                        fp.write(word[0] + '\n')
                # elif MILexicon[word[0]] > threshold_MI and ChLexicon[word[0]] >= threshold_Chi and \
                # LgLexicon[word[0]] > threshold_Lg and RRLexicon[word[0]] > threshold_RR:
                elif ChLexicon[word[0]] >= threshold_Chi and MILexicon[word[0]] > threshold_MI:
                        fp.write(word[0] + '\n')
                        # print(MILexicon[word[0]])
                        # fp.write(word[0] + ' ' + str(word[1]) + '\n')
        fp.close()

def RefineMain(argv):
        Address = './Entry_processed/lexicon_build/discourse/'
        OutputAddress = './Entry_processed/lexicon_build/discourse/'
        MIfilefix = 'voc_'
        Chfilefix = 'voc_chi_square_'
        Outputfix = 'voc_discourse_final_'
        polarizationSet = {'positive','negative'}
        for polar in polarizationSet:
                MILexicon = Counter()
                ChLexicon = Counter()
                LgLexicon = Counter()
                RRLexicon = Counter()
                MIfile = Address + MIfilefix + polar + '_MI.txt'
                Chfile = Address + Chfilefix + polar + '.txt'
                TraverseLexicon(MIfile, MILexicon, polar)
                TraverseLexicon(Chfile, ChLexicon, polar)
                Logfile = Address + MIfilefix + polar + '_Log.txt'
                RRfile = Address + MIfilefix + polar + '_RR.txt'
                TraverseLexicon(Logfile, LgLexicon, polar)
                TraverseLexicon(RRfile, RRLexicon, polar)
                outputFile = OutputAddress + Outputfix + polar + '.txt'
                DecisionMaking(outputFile, MILexicon, ChLexicon, LgLexicon, RRLexicon)

if __name__ == '__main__':
        RefineMain(sys.argv[1:])
