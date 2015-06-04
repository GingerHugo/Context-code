import string  
import re  
import sys
import os

MAXIMUM = 148
Ending_dict = {'。#PU':1, '！#PU':2, '!#PU':3,'?#PU':4,'.#PU':5,'？#PU':6}
Transition_dict = {'，#PU':1,',#PU':2}
Ending = {'。':1, '！':2, '!':3,'?':4,'.':5,'？':6}
Transition = {'，':1,',':2}

def preprocess(fileName, mapping_file, pre_mapping_file):
    Address = 'G:/booking.com/segmented/'
    outputAddress = 'G:/booking.com/segmented/removed/'
    mappingAddress = 'G:/booking.com/segmented/mapping/'
    previousMapping = 'G:/booking.com/filtered/mapping/'
    input_file = open(Address + fileName, 'r', encoding = 'utf-8')
    output_file = open(outputAddress + fileName, 'w', encoding = 'utf-8')
    mapping_file = open(mappingAddress + mapping_file, 'w', encoding = 'utf-8')
    pre_input_file = open(previousMapping + pre_mapping_file,'r',encoding = "utf-8")
    sentences = input_file.readline()
    ID = pre_input_file.readline()
    while sentences:
        sentences = sentences[:-1]
        if len(sentences.split()) < MAXIMUM:
            output_file.write(sentences + '\n')
            mapping_file.write(ID)
        else:
            print(sentences)
        sentences = input_file.readline()
        ID = pre_input_file.readline()
    input_file.close()
    output_file.close()
    mapping_file.close()
    pre_input_file.close()

def Main(argv):
    cityList = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList = ['Paris','Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
    # cityList = ['Beijing']
    cityList4 = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore','Kunming','Huangshan','Jiuzhaigou','Guiyang','Chongqing','Rome','Barcelona']
    AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = cityList4 + AList
    for city in cityList:
        posi_file = city + '_positive_seg.out'
        mapping_file = city + '_positive_mapping_seg.txt'
        pre_mapping_file = city + '_positive_mapping.txt'
        preprocess(posi_file, mapping_file, pre_mapping_file)        
        nega_file = city + '_negative_seg.out'
        mapping_file = city + '_negative_mapping_seg.txt'
        pre_mapping_file = city + '_negative_mapping.txt'
        preprocess(nega_file, mapping_file, pre_mapping_file)


if __name__ == '__main__':
    Main(sys.argv[1:])