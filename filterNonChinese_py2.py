# -*- coding: utf-8 -*-   
import string  
import re  
import sys
import os
import codecs

def filter(input_file_name,output_file_name):
    input_file = codecs.open(input_file_name,'r',"utf-8")
    output_file = codecs.open(output_file_name,'w',"utf-8")
    # print 'Here!'
    for lines in input_file:
        lines = lines[:-1]
        # print lines
        result = re.findall(ur'[\u4e00-\u9fff]+',lines)
        result2 = re.findall(ur'[\u3040-\u30ff]+',lines)
        if result and not result2 and (len(result) > 3 or (len(result) == 1 and len(result[0]) > 2) or (len(result) > 1 and len(result[0]) >= 4)):
            if (len(result) > 1 and len(result) <= 3 and len(result[0]) < 4):
                print result
            words = lines.replace('- ','')
            output_file.write(words + '\n')
    output_file.close()
    input_file.close()

def Main(argv):
    cityList = ['beijing','Chengdu','Guangzhou','HongKong','Shanghai','Xi_an']
    cityList = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
    cityList = ['Paris']
    TaiwanList = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore']
    ChineseList = ['Kunming','Huangshan','Jiuzhaigou']
    ChineseList2 = ['Guiyang','Chongqing']
    EuroupList = ['Rome','Barcelona']
    cityList = TaiwanList + ChineseList + ChineseList2 + EuroupList
    AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = AList
    for city in cityList:
        # city = 'beijing'
        positive_filename = './processed/' + city + '_positive.out'
        negative_filename = './processed/' + city + '_negative.out'

        positive_out_filename = './filtered/' + city + '_positive_filtered.out'
        negative_out_filename = './filtered/' + city + '_negative_filtered.out'
        filter(positive_filename,positive_out_filename)
        filter(negative_filename,negative_out_filename)


if __name__ == '__main__':
    Main(sys.argv[1:])
