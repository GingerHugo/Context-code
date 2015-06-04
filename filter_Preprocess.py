import string  
import re  
import sys
import os

MAXIMUM = 148
Ending_dict = {'。#PU':1, '！#PU':2, '!#PU':3,'?#PU':4,'.#PU':5,'？#PU':6}
Transition_dict = {'，#PU':1,',#PU':2}
Ending = {'。':1, '！':2, '!':3,'?':4,'.':5,'？':6}
Transition = {'，':1,',':2}

def preprocess(fileName, mapping_file):
    Address = 'G:/booking.com/filtered/transfered/'
    outputAddress = 'G:/booking.com/filtered/split/'
    mappingAddress = 'G:/booking.com/filtered/mapping/'
    input_file = open(Address + fileName, 'r', encoding = 'utf-8')
    output_file = open(outputAddress + fileName, 'w', encoding = 'utf-8')
    mapping_file = open(mappingAddress + mapping_file, 'w', encoding = 'utf-8')
    # input_file = open('Beijing_negative_pos.out','r',encoding = "utf-8")
    for lines in input_file:
        # lines = lines[:-1]
        result = lines.partition('|')
        ID = result[0]
        # print(ID)
        content = result[2]
        # sentences = re.search(r"[^。.！!?？]+[^\d。.！!?？]+['\n']", content, re.M|re.I)
        sentences = re.findall(r"[^。.！!?？；;\s]+[^\d。.！!?？；;]+[。.！!?？；;\n]", content, re.M|re.I)
        if sentences:
            for sentence in sentences:
                if sentence[-1] == '\n':
                    sentence = sentence[:-1]
                output_file.write(sentence + '\n')
                mapping_file.write(ID + '\n')
                # print(sentence)
    input_file.close()
    output_file.close()
    mapping_file.close()

def Main(argv):
    cityList = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
    cityList = ['Paris']
    TaiwanList = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore']
    ChineseList = ['Kunming','Huangshan','Jiuzhaigou']
    ChineseList2 = ['Guiyang','Chongqing']
    EuroupList = ['Rome','Barcelona']
    cityList = TaiwanList + ChineseList + ChineseList2 + EuroupList
    AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = cityList + AList
    for city in cityList:
        posi_file = city + '_positive_transfer.out'
        mapping_file = city + '_positive_mapping.txt'
        preprocess(posi_file, mapping_file)        
        nega_file = city + '_negative_transfer.out'
        mapping_file = city + '_negative_mapping.txt'
        preprocess(nega_file, mapping_file)


if __name__ == '__main__':
    Main(sys.argv[1:])