# encoding=utf-8
# Python 3.4
import os
import sys
import math
import urllib.request
import urllib
# import chardet
from bs4 import BeautifulSoup
from html.parser import HTMLParser

aspect = ['清洁程度','舒适程度','酒店地点','设施','员工素质','性价比','WiFi']
group = ['所有评论者','家庭','夫妻','朋友团组','独行客人','商务旅客']

aspect_dict = {'清洁程度':'clean','舒适程度':'comfort','酒店地点':'location','设施':'services','员工素质':'staff','性价比':'value','WiFi':'wifi'}
group_dict = {'所有评论者':'data-total_hotel_','家庭':'data-family_with_children_hotel_','夫妻':'data-couple_hotel_',\
'朋友团组':'data-review_category_group_of_friends_hotel_','独行客人':'data-solo_traveller_hotel_','商务旅客':'data-business_traveller_hotel_'}

def GetWrittenReview(url, outputFile, userID, hotelID):
    # print(url)
    req = urllib.request.Request(url,
    headers = {"Referer": "http://www.booking.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.24 \
        (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24"
    })
    u = urllib.request.urlopen(url = req, timeout = None)
    # print(url)
    buffer_1 = u.read()
    soup = BeautifulSoup(buffer_1)
    result = soup.find("div", attrs = {"class": "review_list_pagination"})
    # print(result)
    nextPage = result.find("p", attrs = {"class": "page_link review_next_page"})
    nextPage = nextPage.find("a", attrs = {"id": "review_next_page_link"})
    # print(nextPage)
    if nextPage:
        newUrl = 'http://www.booking.com' + nextPage["href"]
    else:
        return (False, userID, url)
    result = soup.find("ul", attrs = {"class": "review_list"})
    if result:
        candidates = result.find_all("li", attrs = {"class": "review_item clearfix"}, recursive = False)
        for candidate in candidates:
            candidate = candidate.find("div", attrs = {"class": "review_item_review"}) 
            candidate = candidate.find("div", attrs = {"class": "review_item_review_container lang_ltr"})
            scoreNum = candidate.find("div", attrs = {"class": "review_item_review_header review_item_with_info_tags"})
            scoreNum = scoreNum.find("div", attrs = {"class": "review_item_header_score_container"})
            scoreNum = scoreNum.find("div", attrs = {"class": "review_item_review_score"})
            outputFile.write("Customer total score: " + scoreNum.text.replace('\n','') + '\n')
            case = candidate.find("ul", attrs = {"class": "review_item_info_tags clearfix"})
            cases = case.find_all("li", attrs = {"class": "review_info_tag"}, recursive = False)
            outputFile.write("Label: ")
            for x in range(0,len(cases) - 1):
                outputFile.write(cases[x].text.replace('•','') + '|')                
            outputFile.write(cases[len(cases) - 1].text.replace('•','') + '\n')
            candidate = candidate.find("div", attrs = {"class": "review_item_review_content"})
            headline = candidate.find("p", attrs = {"class": "review_item_headline"})
            comment = candidate.find("p", attrs = {"class": "review_pos"})
            emptyComment = candidate.find("p", attrs = {"class": "review_none"})
            temp = str(userID)
            for x in range(0,4 - len(temp)):
                temp = '0' + temp
            temp = hotelID + '_' + temp
            if headline:
                temphead = headline.text.replace("\"",'')
                outputFile.write(temp + '|' + temphead + '\n')
            else:
                outputFile.write(temp + '|\n')
            if emptyComment:
                outputFile.write('1|\n0|\n')
                userID += 1
                continue
            outputFile.write('1|')
            if comment:
                pre = comment.text.partition('\n')
                after = pre[2].rpartition('\n')
                content = after[0]
                outputFile.write(content.replace('\n',''))
                outputFile.write('\n')
                # print(chardet.detect(content))
            else:
                outputFile.write('\n')
            comment = candidate.find("p", attrs = {"class": "review_neg"})
            outputFile.write('0|')
            if comment:
                pre = comment.text.partition('\n')
                after = pre[2].rpartition('\n')
                content = after[0]
                outputFile.write(content.replace('\n',''))
                outputFile.write('\n')
                # print(content)
            else:
                outputFile.write('\n')
            userID += 1
        return (True, userID, newUrl)
    else:
        return (False, userID, newUrl)

def GetReviewContent(url, url2, initial, DocCount, hotelID):
    # print(url)
    posi_file = './positive_' + str(initial) + '_' + str(DocCount) + '.dat'
    nega_file = './negative_' + str(initial) + '_' + str(DocCount) + '.dat'
    out_File = str(initial) + '_' + hotelID + '.dat'
    share_disk_address = '/shared_disks/nas-2.1/jjwang/'
    u = urllib.request.urlopen(url)
    buffer_1 = u.read()
    soup = BeautifulSoup(buffer_1)
    outputFile = open(out_File,'w', encoding = 'utf-8')
    outputFile.write("Hotel ID: " + hotelID + '\n')
    result = soup.find("div", attrs = {"id": "blockdisplay4"})
    if not result:
        print(url)
        outputFile.close()
        return DocCount
    result = result.find("div", attrs = {"id": "review_list_score_container"})
    result = result.find("div", attrs = {"id": "review_list_score"})
    result = result.find("ul", attrs = {"id": "review_list_score_breakdown"})
    userID = 1

    # Write the score of the hotel
    # Score_breakdown_list = result[""]

    # scores = result.find_all("li", attrs = {"class": "clearfix"}, recursive = False)
    # if scores:
    #     for score in scores:
    #         TitleName = score.find("p", attrs = {"class": "review_score_name"})
    #         ReviewScore = score.find("p", attrs = {"class": "review_score_value"})
    #         outputFile.write(TitleName.text + ' ' + ReviewScore.text + '\n')

    for member in group:
        outputFile.write(member + ': ')
        for eachAspect in aspect:
            item = group_dict[member] + aspect_dict[eachAspect]
            temp = result.get(item,0)
            if temp:
                outputFile.write(eachAspect + ' ' + temp +'|')
        outputFile.write('\n')

    # Write the review
    loopFlag = True
    while loopFlag:
        (loopFlag, userID, newUrl) = GetWrittenReview(url2, outputFile, userID, hotelID)
        url2 = newUrl
        # print(url2)
    outputFile.close()
    u.close()
    DocCount += userID
    return DocCount

def CrawingBookingdotComControl(url, initial, DocCount):
    (result, DocCount) = CrawingBookingdotCom(url, initial, DocCount)
    # print(url)
    # url_original = 'http://www.booking.com/searchresults.zh-cn.html?sid=3e3b4b0439eb4fdd8a4c9667765b95df;dcid=4;city=-1898541;class_interval=1;csflt=%7B%7D;dtdisc=0;hyb_red=0;inac=0;interval_of_time=undef;nha_red=0;redirected_from_city=0;redirected_from_landmark=0;redirected_from_region=0;review_score_group=empty;score_min=0;ss_all=0;ssb=empty;sshis=0&;or_radius=0;;rows=15;offset='
    # http://www.booking.com/reviewlist.zh-cn.html?sid=da567f1d05a564c8d0b9deae82944d2c;dcid=1;pagename=prime;cc1=cn;type=total;dist=1;offset=0;rows=10;rid=&_=1413513871315
    # iCount = 1
    while (result):
        New_url = 'http://www.booking.com' + result.attrs['href']
        # New_url = url_original + str(iCount * 15)
        # iCount += 1
        # print(New_url)
        (result, DocCount) = CrawingBookingdotCom(New_url, initial, DocCount)
    return DocCount

def CrawingBookingdotCom(url, initial, DocCount):
    # print(url)
    urlHeader = 'http://www.booking.com/reviewlist.zh-cn.html?sid=da567f1d05a564c8d0b9deae82944d2c;dcid=1;pagename='
    urlMiddle = ';cc1='
    urlTail = ';type=total;dist=1;offset=0;rows=10;rid=&_='
    urlPost = '#hash-blockdisplay4'
    req = urllib.request.Request(url,
    headers = {"Referer": "http://www.booking.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24"
    })
    u = urllib.request.urlopen(url = req, timeout = None)
    # print(url)
    buffer_1 = u.read()
    soup = BeautifulSoup(buffer_1)
    candidates = soup.find("div", attrs = {"id": "ajaxsrwrap"})
    candidates = candidates.find("div", attrs = {"id": "search_results_table"})
    # candidates = candidates.find("class", attrs = {"id": "search_results_table"})
    

    candidates = candidates.find("div", attrs = {"class": "hotellist"})
    # print(candidates)
    candidates = candidates.find("div", attrs = {"id": "hotellist_inner"})
    # texts = candidates.find_all("div", attrs = {"class": "sr_item clearfix\nhighlight_hover_hotel\nsr_item_no_dates\n"}, recursive = False)
    texts = candidates.find_all("div", attrs = {"class": " sr_item clearfix    highlight_hover_hotel    sr_item_no_dates     "}, recursive = False) 
    if not texts:
        print('Parsing error!!!')
        print(url)
        nextItem = []
        return (nextItem, DocCount)
    for text in texts:
        hotelID = text['data-hotelid']
        # print(hotelID)
        text = text.find("div", attrs = {"class": "sr_item_content"})
        text = text.find("div", attrs = {"class": "reviewFloater"})
        text = text.find("a")
        if text:
            result = text.get('href',0)
            if result:
                url_2 = 'http://www.booking.com' + result
                result = result.partition('.')
                # print(result)
                result = result[0].rpartition('/')
                # url_3 = urlHeader + result[2] + urlMiddle + 'au' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'us' + urlTail + hotelID + urlPost
                url_3 = urlHeader + result[2] + urlMiddle + 'ca' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'jp' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'my' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'sg' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'kr' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'fr' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'it' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'es' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'th' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'cn' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'hk' + urlTail + hotelID + urlPost
                # url_3 = urlHeader + result[2] + urlMiddle + 'tw' + urlTail + hotelID + urlPost
                DocCount = GetReviewContent(url_2, url_3, initial, DocCount, hotelID)
                # print(url_2)
                # print(url_3)
    
    nextItems = soup.find("div", attrs = {"class": "results-paging"})
    if not nextItems:
        return (nextItems, DocCount)
    nextItem = nextItems.find("a", attrs = {"class": "paging-next"})
    # print(nextItem.attrs['href'])
    # print("next page!\n")
    u.close()
    return (nextItem, DocCount)

def CrawingMain(argv):
    TaiwanList = ['Tokyo', 'Kyoto', 'Osaka','Seoul','Busan','KualaLumpur','Bangkok','Pattaya','Singapore']
    ChineseList = ['Kunming','Huangshan','Jiuzhaigou']
    ChineseList2 = ['Guiyang','Chongqing']
    EuroupList = ['Rome','Barcelona']
    # initial = 'Barcelona'
    AList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','Vancouver','Sydney','Melbourne','Brisbane','GoldCoast','Montreal','Quebec','SanDiego','Toronto']
    BList = ['SanFrancisco','NewYork','Seattle','LosAngeles','Boston','SanDiego']
    # for city in ChineseList:
    initial = 'Toronto'
    DocCount = 1
    header = 'http://www.booking.com/searchresults.zh-cn.html?sid=da567f1d05a564c8d0b9deae82944d2c;dcid=1;city=-'
    places = {'Beijing':'1898541', 'Shanghai':'1924465', 'HongKong':'1353149', 'Xi_an':'1931562', \
    'Taipei':'2637882', 'Taichung':'2637824', 'Kaohsiung':'2632378','Guangzhou':'1907161','Guilin':'1907565',\
    'Hangzhou':'1908366','Guiyang':'1907603','Chongqing':'1900774','Chengdu':'1900349','Shenzhen':'1925268',\
    'Bangkok':'3414440','Tokyo':'246227','Hualian':'2631690','Kenting':'2632489','Seoul':'716583','Paris':'1456928',\
    'Barcelona':'372490','Rome':'126693','Nanjing':'1919548','Qingdao':'1922199','Lijiang':'1902900','Dali':'1901829',\
    'Wuhan':'1930776','Kunming':'1913826','Huangshan':'900048301','Jiuzhaigou':'900050018','Pattaya':'3242432','Singapore':'73635',\
    'Osaka':'240905','Kyoto':'235402','KualaLumpur':'2403010','Busan':'713900','SanFrancisco':'20015732','NewYork':'20088325',\
    'Seattle':'20144883','LosAngeles':'20014181','Boston':'20061717','Vancouver':'575268','Sydney':'1603135','Melbourne':'1586844',\
    'Brisbane':'1561728','GoldCoast':'1575736','Montreal':'569541','Quebec':'571851','SanDiego':'20015725','Toronto':'574890'}
    if initial in BList:
        output = CrawingBookingdotComControl(header[:-1] + places[initial] + '&', initial, DocCount)
    else:   
        output = CrawingBookingdotComControl(header + places[initial] + '&', initial, DocCount)
    print(output)
    # test()
    # url = 'http://www.booking.com/hotel/cn/prime.zh-cn.html?tab=4'
    # url = 'http://www.booking.com/hotel/cn/inner-mongolia-grand-wangfujing.zh-cn.html?tab=4'
    # GetReviewContent(url)

if __name__ == '__main__':
    CrawingMain(sys.argv[1:])
