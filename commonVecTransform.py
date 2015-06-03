import string  
import re  
import sys
import os
from collections import *
from math import *
from numpy import array
import numpy as np

dimension = 400

def Transform(Vector_word, fileName, outputFile, flag):
        global dimension
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                with open(outputFile, 'w', encoding = 'utf-8') as outFp:
                        for lines in fp:
                                words = lines[:-1].split()
                                if len(words):
                                        temp = np.zeros(dimension)
                                        for word in words:
                                                temp = np.add(temp,Vector_word[word])
                                                # temp = temp + Vector_word[word]
                                        temp = temp / float(dimension)
                                        outFp.write(str(flag))
                                        if len(temp) != dimension:
                                                print("Vector error")
                                                print(temp)
                                        for x in range(0,dimension):
                                                outFp.write(' ' + str(x + 1) + ':' + str(temp[x]))
                                        outFp.write('\n')
                                                

def ReadInVector(vector_file_name, Vector_word, Lexicon_Corpus, model):
        candidateWord = set(Lexicon_Corpus.keys())
        VectorSet = set()
        with open(vector_file_name, 'r', encoding = 'utf-8') as fp:
                flag = 0
                for lines in fp:
                        if (model != 'Glove') and (not flag):
                                flag = 1
                                continue
                        line = lines[:-1].split()
                        word = line[0].rsplit('/',1)[0]
                        VectorSet.add(word)
                        if word in Lexicon_Corpus:
                                temp = array(line[1:])
                                if len(temp) != 400:
                                        print("error!")
                                        print(len(temp))
                                        temp = temp[1:]
                                Vector_word[word] = temp.astype(np.float, copy=False)
        return (candidateWord - VectorSet)

def GetAllWords(Lexicon, fileName):
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        words = line.split()
                        for word in words:
                                Lexicon[word] += 1

def GetWordCollection(Lexicon, IDFDict, fileName, BanSet1, BanSet2, EntryFlag = True):
        with open(fileName, 'r', encoding = 'utf-8') as fp:
                for lines in fp:
                        line = lines[:-1]
                        # sentence = line.split(' ', 1)[1]
                        sentence = GetSentence(line, EntryFlag)
                        wordBags = set()
                        for word in sentence.split():
                                # candidate = word.rsplit('#', 1)[0]
                                candidate = GetCandiate(word, EntryFlag)
                                if  (candidate not in BanSet1) and (candidate not in BanSet2):
                                        Lexicon[candidate] += 1
                                        wordBags.add(candidate)
                        for word in wordBags:
                                IDFDict[word] += 1

def GetSentence(line, flag):
        if flag:
                sentence = line.split(' ', 1)[1]
        else:
                sentence = line
        return sentence

def GetCandiate(word, flag):
        if flag:
                candidate = word.rsplit('#', 1)[0]
        else:
                candidate = word
        return candidate

def CalculateVocabularySequence(Vocabulary, IDFDict):
        count = 0
        for word in IDFDict:
                count += 1
                Vocabulary[word] = count

def AddOOVVectors(word_vecs, vocab, OOVWord,min_df=1, k=400):
        """
        For words that occur in at least min_df times, create a separate word vector.    
        0.25 is chosen so the unknown vectors have (approximately) same variance as pre-trained ones
        """
        for word in OOVWord:
                if vocab[word] >= min_df:
                        word_vecs[word] = np.random.uniform(-0.25,0.25,k)
        # print(OOVWord)

def transform2vecDNN(argv):
        Vector_word = Counter()
        Lexicon_Corpus = Counter()
        Address = './'
        polarizationSet = {'positive', 'negative'}
        prefix_Set = {'context_'}
        posfix_Set = {'_testing.txt', '_training.txt'}
        for polar in polarizationSet:
                for prefix in prefix_Set:
                        for posfix in posfix_Set:
                                fileName = Address + prefix + polar + posfix
                                GetAllWords(Lexicon_Corpus, fileName)
        vector_file_name = Address + '4300W.vectors.txt'
        ReadInVector(vector_file_name, Vector_word, Lexicon_Corpus)
        for polar in polarizationSet:
                for prefix in prefix_Set:
                        for posfix in posfix_Set:
                                flag = 0
                                fileName = Address + prefix + polar + posfix
                                outputFile = Address + 'experiment_' + polar + '_DNN_Glov' + posfix
                                if polar == 'positive':
                                        flag = 1
                                Transform(Vector_word, fileName, outputFile, flag)


if __name__ == '__main__':
        transform2vecDNN(sys.argv[1:])