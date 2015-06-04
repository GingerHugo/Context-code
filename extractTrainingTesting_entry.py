import sys
import random

def lottery(EntryFile, outputDict):
    with open(EntryFile, 'r', encoding = 'utf-8') as fd:
        for lines in fd:
            line = lines[:-1]
            content = line.partition('|')[2]
            result = random.randint(1,10)
            if result == 10:
                outputDict['testing_total'] = outputDict['testing_total'] + 1
                outputDict['testing'].write(content + '\n')
            else:
                outputDict['training_total'] = outputDict['training_total'] + 1
                outputDict['training'].write(content + '\n')


def ExtractMain(argv):
    cityList1 = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList2 = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian']
    cityList3 = ['Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan','Paris']
    cityList4 = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore','Kunming']
    cityList5 = ['Huangshan','Jiuzhaigou','Guiyang','Chongqing','Rome','Barcelona']
    cityList6 = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane']
    cityList7 = ['GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = cityList1 + cityList2 + cityList3 + cityList4 + cityList5 + cityList6 + cityList7
    EntryFile = 'G:/booking.com/filtered/transfered/'
    # POSTaggFile = 'G:/booking.com/postagged/'
    # ParsingFile = 'G:/booking.com/parseResult/'
    outputFile = 'G:/booking.com/Entry_processed/Entry_original/'
    outputDict = {}
    PolarizedSet = {'positive','negative'}
    for polar in PolarizedSet:
        file1 = outputFile + 'Review_Entry' + '_' + polar + '_training.txt'
        fp1 = open(file1, 'w', encoding = 'utf-8')
        file2 = outputFile + 'Review_Entry' + '_' + polar + '_testing.txt'
        fp2 = open(file2, 'w', encoding = 'utf-8')
        outputDict[polar] = {'training': fp1, 'testing': fp2, 'training_total': 0, 'testing_total': 0}
    # print(outputDict['positive'])

    for city in cityList:
        for polar in PolarizedSet:
            file1 = EntryFile + city + '_' + polar + '_transfer.out'
            lottery(file1, outputDict[polar])

    for polar in PolarizedSet:
        print(polar, "case: ")
        for eachFile in outputDict[polar]:
            if eachFile in {'training_total', 'testing_total'}:
                print(eachFile, " case number: ", outputDict[polar][eachFile])
            else:
                outputDict[polar][eachFile].close()

if __name__ == '__main__':
    ExtractMain(sys.argv[1:])