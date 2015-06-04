import sys
import os
# import opencc

def processing(info, positive_output_file, negative_output_file, headScore_output_file):
    listfile = os.listdir(info)
    for filename in listfile:
        # print(filename)
        print(str(info + filename))
        input_file_address = str(info + filename)
        clustering(input_file_address, positive_output_file, negative_output_file, headScore_output_file)
        # for lines in input_file:
        #     output_file.write(lines)

def clustering(input_file_address, positive_output_file, negative_output_file, headScore_output_file):
    maxThreshold = 10
    input_file = open(input_file_address, 'r', encoding = 'utf-8')
    for x in range(0,7):
        input_file.readline()
    tempStr = input_file.readline()
    tempStr = tempStr[:-1]
    if tempStr:
        score = tempStr.split(':')[1]
        score = score[1:]
        pos_list = []
        neg_list = []
        comment_list = []
        flag = False
        while tempStr:
            input_file.readline()
            tempStr = input_file.readline()
            tempStr = tempStr[:-1]
            hotel_userID = tempStr.split('|')[0]
            if not hotel_userID:
                tempStr = input_file.readline()
                tempStr = tempStr[:-1]
                hotel_userID = tempStr.split('|')[0]
            if len(tempStr.split('|')) < 2:
                print(tempStr)
            commentTitle = tempStr.split('|')[1]
            if commentTitle:
                temp = hotel_userID + '|' + score + '|' + commentTitle
                while 1:
                    tempStr = input_file.readline()
                    tempStr = tempStr[:-1]
                    if len(tempStr.split('|')) == 1:
                        temp += tempStr
                    else:
                        comment_list.append(temp)
                        positive_content = tempStr.split('|')[1]
                        break
            else:
                tempStr = input_file.readline()
                tempStr = tempStr[:-1]
                positive_content = tempStr.split('|')[1]
            if positive_content:
                while 1:
                    tempStr = input_file.readline()
                    tempStr = tempStr[:-1]
                    temp = tempStr.split('|')
                    if len(temp) == 1:
                        positive_content += tempStr
                    elif temp[0] != '0':
                        positive_content += tempStr
                    else:
                        negative_content = temp[1]
                        break
            else:
                tempStr = input_file.readline()
                tempStr = tempStr[:-1]
                negative_content = tempStr.split('|')[1]
            if negative_content:
                while 1:
                    tempStr = input_file.readline()
                    tempStr = tempStr[:-1]
                    if tempStr:
                        temp = tempStr.split(':')[0]
                        if (temp == 'Customer total score'):
                            score = tempStr.split(':')[1]
                            score = score[1:]
                            flag = False
                            break                        
                        else:
                            negative_content += tempStr
                    else:
                        flag = True
                        break
            else:
                tempStr = input_file.readline()
                tempStr = tempStr[:-1]
            if positive_content:
                # print(positive_content)
                positive_content = hotel_userID + '|' + positive_content 
                pos_list.append(positive_content)
            if negative_content:
                negative_content = hotel_userID + '|' + negative_content
                neg_list.append(negative_content)
            if flag:
                break
        if ((len(pos_list) >= maxThreshold) and (len(neg_list) >= maxThreshold)):
            for positive_content in pos_list:
                positive_output_file.write(positive_content + '\n')
            for negative_content in neg_list:
                negative_output_file.write(negative_content + '\n')
            for comment_content in comment_list:
                headScore_output_file.write(comment_content + '\n')

def writeBat(transfer_file, file_transfered, bat_File):
    bat_File.write('opencc -i G:/booking.com/filtered/' + transfer_file + ' -o G:/booking.com/filtered/transfered/' + \
        file_transfered + ' -c zht2zhs.ini\n')

def Main(argv):
    # listfile = os.getcwd()
    cityList = ['HongKong','Beijing','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList = ['Taipei','Kaohsiung','Shanghai','Xi_an','Guangzhou','Chengdu']
    cityList = ['Taipei','Kaohsiung','Dali','Guilin','Hangzhou','Hualian','Kenting','Lijiang','Nanjing','Qingdao','Shenzhen','Wuhan']
    cityList = ['Paris']
    TaiwanList = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore']
    ChineseList = ['Kunming','Huangshan','Jiuzhaigou']
    ChineseList2 = ['Guiyang','Chongqing']
    EuroupList = ['Rome','Barcelona']
    cityList = TaiwanList + ChineseList + ChineseList2 + EuroupList
    AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    cityList = AList
    bat_File = open('convert.bat','w', encoding = 'utf-8')
    bat_File.write('G:\ncd G:/booking.com/opencc-0.4.2\n')
    shell_seg_File = open('segmentSentence.sh','w', encoding = 'utf-8')
    shell_pos_File = open('POSTagSentence.sh','w', encoding = 'utf-8') 
    # print('here')
    for city in cityList:
        shell_parse_File = open( city + '_ParseSentence.sh','w', encoding = 'utf-8')
        # city = 'HongKong'
        file_dire = "G:\\booking.com\\" + city + "\\"
        # # negative_dire = "E:\\NLP相关\\booking.com\\HongKong_nega\\"
        positive_file = city + '_positive.out'
        negative_file = city + '_negative.out'
        positive_file_filtered = city + '_positive_filtered.out'
        negative_file_filtered = city + '_negative_filtered.out'
        positive_file_transfer = city + '_positive_transfer.out'
        negative_file_transfer = city + '_negative_transfer.out'
        positive_file_seg = city + '_positive_seg.out'
        negative_file_seg = city + '_negative_seg.out'
        positive_file_pos = city + '_positive_pos.out'
        negative_file_pos = city + '_negative_pos.out'
        headScore_file = city + '_headline.out'
        positive_output_file = open(positive_file, 'w', encoding = 'utf-8')
        negative_output_file = open(negative_file, 'w', encoding = 'utf-8')
        headScore_output_file = open(headScore_file, 'w', encoding = 'utf-8')
        processing(file_dire, positive_output_file, negative_output_file, headScore_output_file)
        positive_output_file.close()
        negative_output_file.close()
        headScore_output_file.close()
        writeBat(positive_file_filtered, positive_file_transfer, bat_File)
        shell_seg_File.write("./stanford-segmenter-2014-08-27/segment.sh ctb " + positive_file_transfer + ' UTF-8 0 > ' + positive_file_seg + '\n')
        shell_pos_File.write("./stanford-postagger.sh ./models/chinese-distsim.tagger " + positive_file_seg + ' > ' + positive_file_pos + '\n')
        shell_parse_File.write('./stanford-parser-full-2014-08-27/lexparser-lang_dependency.sh Chinese 1000 edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz parse_result_positive' + city + ' ' + positive_file_seg + '\n')
        writeBat(negative_file_filtered, negative_file_transfer, bat_File)
        shell_seg_File.write("./stanford-segmenter-2014-08-27/segment.sh ctb " + negative_file_transfer + ' UTF-8 0 > ' + negative_file_seg + '\n')
        shell_pos_File.write("./stanford-postagger.sh ./models/chinese-distsim.tagger " + negative_file_seg + ' > ' + negative_file_pos + '\n')
        shell_parse_File.write('./stanford-parser-full-2014-08-27/lexparser-lang_dependency.sh Chinese 1000 edu/stanford/nlp/models/lexparser/chineseFactored.ser.gz parse_result_negative' + city + ' ' + negative_file_seg + '\n')
        shell_parse_File.close()
    shell_seg_File.close()
    shell_pos_File.close()
    bat_File.close()


if __name__ == '__main__':
    Main(sys.argv[1:])