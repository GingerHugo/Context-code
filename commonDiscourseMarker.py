from collections import *
from nltk.tree import *

def PriorityFiltering(candidate, MarkerGroup):
        if not len(candidate):
                return
        if len(candidate) == 1:
                MarkerGroup.append(candidate.pop())
                return
        workset = set()
        candidate.sort(key=lambda t: t[2])
        # if len(candidate) > 3:
        #         print("Before Filtering")
        #         print(candidate)
        while len(candidate):
                temp = candidate.pop()
                if (set(temp[1]) & workset) and (temp[0][0] and temp[0][1]):
                        continue
                elif (temp[1][1] in workset) and (temp[0][1]):      # '___,但是' case
                        continue
                elif (temp[1][0] in workset) and (temp[0][0]):      # '虽然,___' case
                        continue
                else:
                        if len(candidate):
                                for x in range(-1, -(len(candidate) + 1), -1):
                                        # Using probability as filtering criteria
                                        if candidate[x][2] < temp[2]:
                                                workset |= set(temp[1])
                                                MarkerGroup.append(temp)
                                                break
                                        # Pick the nearest marker
                                        elif (candidate[x][1][0] == temp[1][0]) and (candidate[x][1][1] < temp[1][1]) and (temp[0][1]):
                                                swapTemp = temp
                                                temp = candidate[x]
                                                candidate[x] = swapTemp
                                        elif (candidate[x][1][1] == temp[1][1]) and (candidate[x][1][0] > temp[1][0]) and (temp[0][0]):
                                                swapTemp = temp
                                                temp = candidate[x]
                                                candidate[x] = swapTemp
                        else:
                                MarkerGroup.append(temp)

def SeekVP(leaf, direction):
        EndingSet = {'IP','VP','ROOT'}
        offset = 0
        flag = 2 * direction - 1
        if not leaf:
                print("Impossible case! Leaf error!!!\nERROR\n")
                return 0
        while 1:
                offset += (len(leaf.leaves()) * flag)
                if leaf.label() in EndingSet:
                        offset += (1 * (1 - direction))
                        return offset
                for subtree in leaf.subtrees(lambda t: t.label() in EndingSet):
                        offset += (1 * (1 - direction)) 
                        return offset
                if direction:
                        while (leaf.right_sibling() == None):
                                leaf = leaf.parent()
                                if leaf.label() == 'ROOT':
                                        offset += (1 * (1 - direction)) 
                                        return offset
                        leaf = leaf.right_sibling()
                else:
                        while (leaf.left_sibling() == None):
                                leaf = leaf.parent()
                                if leaf.label() == 'ROOT':
                                        offset += (1 * (1 - direction)) 
                                        return offset
                        leaf = leaf.left_sibling()

def GetSingleMarkerRange(temp, ptree, IP_range_set):
        Index = ptree.treepositions('leaves')
        sentenceLength = len(ptree.leaves())
        if temp[0][0]:          # ('虽然', '') case
                position = int(temp[1][0])
        else:                           # ('', '但是') case
                position = int(temp[1][1])
        left = 0
        right = sentenceLength
        if position in IP_range_set:      # In the head of one main IP
                for y in IP_range_set:
                        if (y > position) and (y < right):
                                right = y
                        elif (y < position) and (y > left):
                                left = y
                right -= 1                                      # PU case
                return(left, position, right)
        else:                           # In the IP
                TreePosition = Index[position]
                leafIndex = tuple(TreePosition[x] \
                        for x in range(0 , len(TreePosition) - 1))
                leaf = ptree[leafIndex]
                offset = SeekVP(leaf, 1)
                right = position + offset
                if temp[0][1]:              # ('', '但是') case
                        offset = SeekVP(leaf, 0)
                        left = position + offset
                return(left, position, right)

def RangeModify(IP_range_set, MarkerGroup, Marker_range_set, ptree):
        if len(MarkerGroup) < 1:
                # if len(MarkerGroup) == 1:
                #         Marker_range_set |= set(range(int(MarkerGroup[0][1][0]), int(MarkerGroup[0][1][1])))
                return
        singleMarkerPool = []
        sentenceLength = len(ptree.leaves())
        for x in range(0, len(MarkerGroup)):
                temp = MarkerGroup[x]
                if (not temp[0][0]) or (not temp[0][1]):
                        singleMarkerPool.append(temp)
                        continue
                if set(range(int(temp[1][0]), int(temp[1][1]))) & Marker_range_set:
                        if int(temp[1][0]) not in Marker_range_set:         # head is not in the range
                                for x in range(int(temp[1][0]), int(temp[1][1])):
                                        if x in Marker_range_set:
                                                break
                                        else:
                                                Marker_range_set |= {x}
                        if int(temp[1][1]) in Marker_range_set:             # tail is in the range
                                for x in range(int(temp[1][1]), sentenceLength):
                                        if x in Marker_range_set:
                                                Marker_range_set -= {x}
                                        else:
                                                break
                else:                           # no overlap add directly
                        Marker_range_set |= set(range(int(temp[1][0]), int(temp[1][1])))
        if singleMarkerPool:
                for x in range(0, len(singleMarkerPool)):
                        temp = singleMarkerPool[x]
                        rangeSingleMarkerTemp = GetSingleMarkerRange(temp, ptree, IP_range_set)
                        # print("Single Marker case!")
                        # print(temp)
                        # print(rangeSingleMarkerTemp)
                        if temp[0][0]:                              # ('虽然', '') case
                                left = rangeSingleMarkerTemp[1]
                                right = rangeSingleMarkerTemp[2]
                                ending = sentenceLength
                        else:                                                           # ('', '但是') case
                                left = rangeSingleMarkerTemp[0]
                                right = rangeSingleMarkerTemp[1]
                                ending = rangeSingleMarkerTemp[2]
                        if set(range(int(left), int(right))) & Marker_range_set:
                                if int(left) not in Marker_range_set:                   # head is not in the range
                                        for x in range(left, right):
                                                if x in Marker_range_set:
                                                        break
                                                else:
                                                        Marker_range_set |= {x}
                                if (int(right) in Marker_range_set) and temp[0][1]:     # tail is in the range and ('', '但是') case
                                        for x in range(right, ending):
                                                if x in Marker_range_set:
                                                        Marker_range_set -= {x}
                                                else:
                                                        break
                        else:                                                       # no overlap add directly
                                Marker_range_set |= set(range(int(left), int(right)))

def GetIPHeadSet(IP_range_set, IP_range):
        for count in IP_range:
                IP_range_set.add(int(IP_range[count][0]))

def PriorityDecision(detected, IP_range, IP_range_label, ptree, Marker_range_set):       # previous_state = 0 same as label, = 1 reverse
        MarkerGroup = []
        candidate = list(detected)      # detected is a list of tuples which contains (marker, pair range, probability) 
        threshold = len(candidate)
        PriorityFiltering(candidate, MarkerGroup)
        IP_range_set = set()
        GetIPHeadSet(IP_range_set, IP_range)
        RangeModify(IP_range_set, MarkerGroup, Marker_range_set, ptree)
        # if threshold > 0:
        #         print("Test")
        #         print(ptree.leaves())
        #         print(MarkerGroup)
        #         print(Marker_range_set)
        previous_state = 0
        for IP_number in IP_range:
                temp = IP_range[IP_number]
                count = 0
                it = temp[0]
                for x in range(temp[0],temp[1]):
                        flag = 0
                        if x in Marker_range_set:
                                flag = 1
                                if 1 != previous_state:
                                        if x != temp[0]:
                                                IP_range_label[IP_number][count] = (it, x, previous_state)
                                                count += 1
                                                # if threshold > 3:
                                                #         print(it, x)
                                        it = x
                                        previous_state = 1
                        if not flag:
                                if 0 != previous_state:
                                        IP_range_label[IP_number][count] = (it, x, previous_state)
                                        # if threshold > 3:
                                        #         print(it, x)
                                        it = x
                                        previous_state = 0
                                        count += 1
                IP_range_label[IP_number][count] = (it, x + 1, previous_state)
                # if threshold > 3:
                #         print(it, x + 1)

def GetIPRange(ptree, IP_range):
        # Dive into the tree
        flag = 1
        ParentGroup = deque()
        IPGroup = []
        count = 0
        for child in ptree:
                if child.label() != 'IP':
                        flag = 0
                        break
                else:
                        ParentGroup.append(child)
        if not flag:
                for child in ptree:
                        IPGroup.append(child)
        for x in range(0, len(ParentGroup)):
                tempTree = ParentGroup.popleft()
                for child in tempTree:
                        IPGroup.append(child)
        # Traverse the tree
        it = 0
        for child in IPGroup:
                if child.label() != 'PU':
                        IP_range[count] = (it, it + len(child.leaves()))
                        it += len(child.leaves())
                        count += 1
                else:
                        it += 1

def ReadInNegator(negator_set, path):
        with open(path, 'r', encoding = 'utf-8') as fp:
                for line in fp:
                        negator_set.add(line[:-1])

def CheckNegator(leaf, negator_set):
        flag = 0
        if leaf.left_sibling() and leaf.left_sibling().label() != 'PU':
                temp = leaf.left_sibling()
                if set(temp.leaves()) & negator_set:
                        flag = flag^1
                else:
                        flag = flag^0
                if temp.left_sibling() and temp.left_sibling().label() != 'PU':
                        tmp = temp.left_sibling()
                        if set(tmp.leaves()) & negator_set:
                                flag = flag^1
                        else:
                                flag = flag^0
                        return flag
                else:
                        return flag
        else:
                return flag

def CheckNegatorFromDP(word, index, DPResult, negator_set):
        left = word + '-' + str(index + 1)
        if not DPResult.get(left, 0):
                return 0
        count = 0
        for element in DPResult[left]:
                if DPResult[left][element] == 'neg':
                        count += 1
                elif element in negator_set:
                        count += 1
        return (count % 2)

def CheckVP(leaf):
        Plabel = leaf.parent().label()
        while Plabel != 'IP' and Plabel != 'ROOT':
                if Plabel == 'VP':
                        return 1
                else:
                        leaf = leaf.parent()
                        # print(leaf)
                        Plabel = leaf.label()
                        # print(Plabel)
        return 0

def ParseTheDPResult(DPResult, dpline):
        temp = dpline[1:-1].split(',')
        for x in range(0, len(temp)):
                if not (x % 2):
                        tag = temp[x].split('(',1)[0]
                        left = temp[x].split('(',1)[1]
                else:
                        right = temp[x][1:-1].rsplit('-')[0]
                        if not DPResult.get(left, 0):
                                DPResult[left][right] = tag
                        elif not DPResult[left].get(right, 0):
                                DPResult[left][right] = tag
                        else:
                                if tag == 'neg':
                                        DPResult[left][right] = tag