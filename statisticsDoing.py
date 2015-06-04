import string  
import re  
import sys
import os
import itertools

cityList1 = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
cityList2 = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
cityList3 = ['Paris']
TaiwanList = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore']
ChineseList = ['Kunming','Huangshan','Jiuzhaigou']
ChineseList2 = ['Guiyang','Chongqing']
EuroupList = ['Rome','Barcelona']
cityList4 = TaiwanList + ChineseList + ChineseList2 + EuroupList
cityList4 = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore','Kunming','Huangshan','Jiuzhaigou','Guiyang','Chongqing','Rome','Barcelona']
AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
cityList5 = AList
cityList = cityList1 + cityList2 + cityList3 + cityList4 + cityList5
# cityList = cityList1

Address = 'G:/booking.com/filtered/transfered/'
Before_address = 'G:/booking.com/processed/'
positive_case = 0
negative_case = 0

for city in cityList:
    positive_file_transfer = city + '_positive.out' 
    input_file = open(Before_address + positive_file_transfer, 'r', encoding = 'utf-8')
    for lines in input_file:
        positive_case += 1
    input_file.close()   
    negative_file_transfer = city + '_negative.out'
    input_file = open(Before_address + negative_file_transfer, 'r', encoding = 'utf-8')
    for lines in input_file:
        negative_case += 1
    input_file.close()

print("Positive case before filtering is ", positive_case)
print("Negative case before filtering is ", negative_case)

positive_case = 0
negative_case = 0

for city in cityList:
    positive_file_transfer = city + '_positive_transfer.out' 
    input_file = open(Address + positive_file_transfer, 'r', encoding = 'utf-8')
    for lines in input_file:
        positive_case += 1
    input_file.close()   
    negative_file_transfer = city + '_negative_transfer.out'
    input_file = open(Address + negative_file_transfer, 'r', encoding = 'utf-8')
    for lines in input_file:
        negative_case += 1
    input_file.close()

print("Positive case after filtering is ", positive_case)
print("Negative case after filtering is ", negative_case)

totalLenghth = 0
lineNumber = 0
MaxLength = 0

def TraverseDocument(fp):
    global MaxLength
    global lineNumber
    global totalLenghth
    for lines in fp:
        lineNumber += 1
        line = lines[:-1]
        count = len(line.split())
        totalLenghth += count
        if count > MaxLength:
            MaxLength = count

Address = './Entry_processed/Entry_segmented/'
polarSet = {'positive', 'negative'}
typeSet = {'_training', '_testing'}
prefix = 'Segmented_Entry_'
postfix = '.txt'
fileNames = itertools.product(polarSet, typeSet)
for fileName in fileNames:
    with open(Address + prefix + fileName[0] + fileName[1] + postfix, 'r', encoding = 'utf-8') as fp:
        TraverseDocument(fp)
print(MaxLength)
print(totalLenghth / lineNumber)