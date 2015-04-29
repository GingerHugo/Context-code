from collections import *
import string  
import re
from numpy import array
import numpy as np
from nltk.tree import *
from queue import *


# import linkage
import DiscourseMarker

ClauseSet = {'IP','CP'}

d = DiscourseMarker.LinkageDetector('./connectives.csv')

with open('./FullPasingResult_Bangkok_negative_seg.out', 'r', encoding = 'utf-8') as fp:
    with open('./Discourse_Bangkok_negative.txt', 'w', encoding = 'utf-8') as fp2:
        for lines in fp:
            line = lines[:-1]
            if not line.startswith('(ROOT'):
                continue
            tree = Tree.fromstring(line)
            ptree = ParentedTree.convert(tree)
            sentence = ptree.leaves()
            detected = list(d.detect_by_tokens(sentence))
            if detected:
                    print(detected)
                    fp2.write(line + '\n')


# def test():
#     items = ['adada','bsajsk','dkdkc','d344']
#     print(tuple(','.join(item) for item in items)) 

# test()

# item = []
# item.append('{}[{}:{}]'.format(1, 0, 5))
# item.append('{}[{}:{}]'.format(2, 0, 8))
# for element in item:
#     for key in element:
#         print(key)

# map_temp = {}
# map_temp[1] = 2
# map_temp[3] = 4
# print(map_temp)

# f = ['a b', 'c d', 'e f']
# temp = {tuple(l.split()) for l in f}
# print(temp)
# print(f)
# print(','.join('item'))
# temp = 'abcdadas,，扯淡'
# if temp.startswith('abc'):
#     print('here!')

# if re.search(r'\W', temp) is not None:
#     print("Here~~~~")

# A = array([1, 2, 3])
# D = np.zeros((1, 3))
# B = D + A
# C = B * 3
# print(B)
# print(C)

# string_ = '0.83747 0.37747 0.474747'
# string_B = '0.83747 0.37747 0.474747'

# B = array(string_.split())
# A = array(string_B.split())
# A = A.astype(np.float)
# B = B.astype(np.float)
# # B = array(float(string_))
# print(A.shape)
# print(B.shape)

# temp = np.add(B,A)
# print(B)
# print(A)
# temp = np.zeros(10)
# print(temp)


# A = array([1,0,1])
# B = array([1,1,1])
# print(sum(A == B))

# a = OrderedDict()
# a[1] = 4
# a[2] = 3
# a[3] = 1
# print(a)

# a = {}

# if a.get(1,0):
#     print("error!!")


# with open('G:/booking.com/FullParsingResult/FullPasingResult_Bangkok_negative_seg.out','r',encoding = 'utf-8') as fp:
#     count = 1
#     DisplaySet = {}
#     for lines in fp:
#         ClauseSet = {'IP','CP'}
#         line = lines[:-1]
#         tree = Tree.fromstring(line)
#         ptree = ParentedTree.convert(tree)
#         tempContext = Queue()
#         print(tree)
#         for index in range(0,len(ptree[0])):
#             # print('count', count)
#             # print('length', len(ptree[0]))
#             # tempContext.put(ptree[0][index])
#             # tempContext.get(ptree[0][index])
#             # for s in ptree[0][index].subtrees(lambda t: t.label() == 'VP'):
#             #     print(s)
#             if ptree[0][index].subtrees(lambda t: t.label() == 'VP'):
#                 DisplaySet[count] = 1
#             # print('index',index)
#             # for pos in ptree[0][index].treepositions('leaves'):
#             #     print(ptree[0][index][pos].label())
#             # ptree[0][x]
#         count += 1
#         # break
#         if count > 5:
#             print(DisplaySet.keys())
#             break
#         # print(ptree.label())
#         # print(ptree[0].label())
#         # print(len(ptree[0]))
#         # print(ptree[0][0].label())
#         # print(ptree[0][1].label())

#         # print(len(ptree[0]))
#         # print(ptree[0])
#         # print(ptree[0][0])
#         # print(ptree[0][0].leaves())


#         # ptree = ParentedTree.fromstring(line)
#         # for subtree in ptree.subtrees():
#         #     print(subtree.leaves())
#             # for subtree_2 in subtree.subtrees():
#             #     print(subtree.treeposition())
#                 # print(subtree_2.parent_index())



# # from collections import *
# # a = Counter()
# # a['a'] = temp

# a = '1212|sadashdahsks|dhasdhadhas'
# c = a.partition('|')
# print(c[2])


# list_a = []

# line = '(ROOT (IP (IP (NP (NN 房间)) (VP (VP (VP (VP (VP (VP (VP (VA 小)) (PU ，) (IP (NP (NN 设施)) (VP (VA 差)))) (PU ，) (VP (VE 没有) (VP (VV 吹风))) (PU ，) (VP (VE 没有) (NP (NN 电视)))) (PU ，) (VP (VV 洗漱) (NP (NN 用品)))) (VP (ADVP (AD 也)) (ADVP (AD 不)) (VP (VA 齐全)))) (PU ，) (VP (VP (ADVP (AD 连续)) (VP (VV 住) (NP (QP (CD 几)) (NP (NN 晚))))) (VP (ADVP (AD 都)) (ADVP (AD 不)) (VP (VV 打扫))))) (PU ，) (VP (ADVP (AD 也)) (VP (VP (VE 没有) (NP (NN 地方))) (VP (VV 凉) (NP (NN 衣服))))))) (PU ，) (IP (NP (NN 房间)) (VP (VP (PP (P 在) (NP (NP (QP (OD 五)) (NP (NN 楼))) (NP (NN 木梯)))) (VP (ADVP (AD 很)) (VP (VV 陡爬) (NP (NN 楼))))) (VP (ADVP (AD 很)) (ADVP (AD 不)) (VP (VA 方便))))) (PU ，) (IP (NP (NN 早餐)) (ADVP (AD 就是)) (NP (QP (CD 三) (CLP (M 块))) (NP (NN 面包片))) (PU ，) (NP (NN 服务)) (VP (ADVP (AD 也)) (ADVP (AD 很)) (VP (VA 差)))) (PU ，) (CP (IP (IP (NP (NN 押金) (NN 收条)) (VP (VV 掉) (AS 了))) (VP (ADVP (AD 都)) (VP (ADVP (AD 不)) (NP (NN 押金))))) (SP 了)) (PU ，) (IP (NP (NN 房间) (NN 价格)) (VP (ADVP (AD 也)) (ADVP (AD 不)) (VP (VA 便宜)))) (PU ，) (IP (VP (ADVP (AD 总之)) (VP (VC 是) (NP (CP (IP (NP (DP (DT 这) (CLP (M 次))) (DNP (NP (NR 泰国)) (DEG 之)) (NP (NN 行))) (VP (ADVP (AD 最)) (ADVP (AD 不)) (VP (VA 满意)))) (DEC 的)) (NP (NN 酒店)))))) (PU ！)))'
# # line = '(ROOT (IP (IP (NP (NN 食物)) (VP (VV 补充) (IP (VP (ADVP (AD 挺)) (VP (VA 快)))))) (PU ，) (IP (ADVP (AD 但是)) (NP (NN 餐具) (CC 和) (NN 饮品)) (VP (ADVP (AD 就)) (VP (VA 慢)))) (PU 。)))'
# tree = Tree.fromstring(line)
# ptree = ParentedTree.convert(tree)
# for x in range(0,len(ptree)):
#     for y in range(0,len(ptree[x])):
#         print(y)
#         # print(ptree[x][y].treeposition())
#         # print(ptree[x][y].pos())
#         # print(len(ptree[x][y]))
#         # print(ptree[x][y].leaf_treeposition(0))
#         # print(ptree[x][y].leaves())
#         if ptree[x][y].pos()[0][1] != 'PU':
#             # for child in ptree[x][y]:
#             #     print(child)
#             #     if child.left_sibling():
#             #         print(child.left_sibling())
#             #         if child.left_sibling().left_sibling():
#             #             print(child.left_sibling().left_sibling())
#             # print(ptree[x][y])
#             print(ptree[x][y][0])
#             print(ptree[x][y][0][0])
#             print(ptree[x][y][0][0].label())
#             # print(ptree[x][y].treepositions('leaves'))
#             # print(ptree[x][y].pos())
#             # print(len(ptree[x][y].treepositions('leaves')))
#             # print(len(ptree[x][y].pos()))
#             # print(ptree[x][y].leaf_treeposition())
#             # print(ptree[x][y][ptree[x][y].leaf_treeposition(0)])
#             # print(ptree[x][y][0])
#             # print(ptree[x][y])
#             # print(ptree[ptree[x][y].leaf_treeposition(0)].left_sibling())
        

# print(tree)


# lines = '2#CD 、#PU 刚#AD 开始#VV 打#VV 电话#NN 的#DEC 时候#NN ,#PU 旅馆#NN 负责人#NN 接#VV 电话#NN 的#DEC 态度#NN 比较#AD 满意#VA ，#PU 但#AD 在#P 晚上#NT 见面#VV 后#LC ，#PU 得知#VV 对#P 这样#AD 打#VV 电话#NN ，#PU 他们#PN 觉得#VV 给#P 他们#PN 填#VV 了#AS 很大#JJ 的#DEG 麻烦#NN 。#PU'

# # result = re.split('，#PU|,#PU', lines)

# # print(result)

# # temp = set(result)
# # print(temp)

# temp = '2#CD 、#PU 刚#AD 开始#VV 打#VV 电话#NN 的#DEC 时候#NN'
# temp2 = '2#CD 、#PU 刚#AD 开始#VV 打#VV 电话#NN 的#DEC 时候#NN ,#PU 旅馆#NN 负责人#NN 接#VV '
# p = re.compile( '(，|,)')
# print(p.sub('',temp))
# print(p.sub('',temp2))

# a = set()
# b = set('dada')
# c = set('dadas')
# a.add(b)
# a.add(c)







# docs = defaultdict(lambda: defaultdict(str))
# docs[1]['a'] = 1
# docs[1]['b'] = 'dada'
# docs[2]['b'] = 1
# print(docs[1]['a'])
# print(docs[1]['b'])

# temp = Counter()
# temp['a'] = 1
# print(temp['b'])
# print(temp['a'])
# print(temp['c'])

# a = '今天天气不是很好，所以都不能出去玩。hdiahdoa'
# sentences = re.findall(r"[^。.！!?？；;\s]+[^\d。.！!?？；;]+[,，]+[^\d。.！!?？；;]+[。.！!?？；;\n]", a, re.M|re.I)
# if sentences:
#     for sentence in sentences:
#         if sentence[-1] == '\n':
#             sentence = sentence[:-1]
#         if re.split('，|,',sentence):
#             context = re.split('，|,',sentence)[0]
#             print(context)


# import os
# from multiprocessing import Process

# def f_sample(name):
#     print('hello', name)
#     print("here!!!")

# if __name__ == '__main__':
#     p = Process(target=f_sample, args=('bob',))
#     p.start()
#     # print("hello")
#     Q = Process(target=f_sample, args=('Alice',))
#     Q.start()
#     p.join()
#     Q.join()


# def strQ2B(ustring):
#     """把字符串全角转半角"""
#     rstring = ""
#     for uchar in ustring:
#         inside_code=ord(uchar)
#         if inside_code==0x3000:
#             inside_code=0x0020
#         else:
#             inside_code-=0xfee0
#         if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符返回原来的字符
#             rstring += uchar
#         else:
#             rstring += chr(inside_code)
#     return rstring

# def strB2Q(ustring):
#     """把字符串半角转全角"""
#     rstring = ""
#     for uchar in ustring:
#         inside_code=ord(uchar)
#         if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符就返回原来的字符
#             rstring += uchar
#         else:
#             if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
#                 inside_code=0x3000
#             else:
#                 inside_code+=0xfee0
#             rstring += chr(inside_code)
#     return rstring


# def B2Q(uchar): 
#     '''半角转全角''' 
#     inside_code=ord(uchar)
#     if inside_code<0x0020 or inside_code>0x7e:
#         return uchar
#     if inside_code==0x0020:
#         inside_code=0x3000
#     else:
#         inside_code+=0xfee0
#     return chr(inside_code)
    
# def stringB2Q(ustring):
#     '''全角转半角'''
#     return "".join([B2Q(uchar) for uchar in ustring])

# def Q2B(uchar):
#     '''全角转半角'''
#     inside_code=ord(uchar)
#     if inside_code==0x3000:
#         inside_code=0x0020
#     else:
#         inside_code-=0xfee0
#     if inside_code<0x0020 or inside_code>0x7e:
#         return uchar
#     return chr(inside_code)

# def stringQ2B(ustring):
#     '''半角转全角'''
#     return "".join([Q2B(uchar) for uchar in ustring])

# a = strB2Q("abc12345真神奇早@@有D尘")
# print (a)
# b = strQ2B(a)
# print (b)
