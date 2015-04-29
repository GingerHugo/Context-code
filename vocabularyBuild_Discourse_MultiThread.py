import DiscourseMarker
from collections import *
from nltk.tree import *
from math import *
import sys
import threading
from commonDiscourseMarker import *
from commonIO import *
import queue

class myThread (threading.Thread):
        def __init__(self, threadID, name, counter, fp, fp2, flag, Ptotal, Ntotal):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.counter = counter
                self.fp = fp
                self.fp2 = fp2
                self.flag = flag
                self.Ptotal = Ptotal
                self.Ntotal = Ntotal
        def run(self):          #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
                global POSset
                global EntryCount
                global WordCount
                global negator_set
                threadLock.acquire()
                detector = DiscourseMarker.LinkageDetector('./Entry_processed/connectives.csv')
                line = self.fp.readline()
                dpline = self.fp.readline()
                threadLock.release()
                while line:
                        line = line[:-1]
                        if not line.startswith('(ROOT'):
                                threadLock.acquire()
                                line = self.fp.readline()
                                threadLock.release()
                                continue
                        try:
                                ptree = ParentedTree.fromstring(line)
                        except:
                                # print(count_line)
                                line = line.replace('(PU )','(PU ）')
                                line = line.replace('(PU (','(PU （')
                                ptree = ParentedTree.fromstring(line)
                        else:
                                pass
                        # ptree = ParentedTree.fromstring(line)
                        sentence = ptree.leaves()
                        sequence = ptree.pos()
                        Index = ptree.treepositions('leaves')
                        IP_range = {}
                        GetIPRange(ptree, IP_range)
                        DiscourseLabel = defaultdict(dict)
                        Marker_range_set = set()
                        PriorityDecision(detector.detect_by_tokens(sentence), \
                                IP_range, DiscourseLabel, ptree, Marker_range_set)
                        DPResult = defaultdict(dict)
                        ParseTheDPResult(DPResult, dpline)
                        for clause_number in DiscourseLabel:
                                for count in DiscourseLabel[clause_number]:
                                        EachPart = DiscourseLabel[clause_number][count]
                                        Discourse_flag = EachPart[2]
                                        # word_set = set()
                                        # print()
                                        for index in range(EachPart[0], EachPart[1]):
                                                if sequence[index][1] in POSset:
                                                        TreePosition = Index[index]
                                                        leafIndex = tuple(TreePosition[x] \
                                                                for x in range(0 , len(TreePosition) - 1))
                                                        leaf = ptree[leafIndex]
                                                        # print(TreePosition)
                                                        # print(leafIndex)
                                                        if CheckVP(leaf):
                                                                Negatorflag = CheckNegatorFromDP(sequence[index][0], index, DPResult, negator_set)
                                                                final = (Negatorflag^(self.flag)^Discourse_flag)
                                                                # if sequence[index][0] not in word_set:
                                                                threadLock.acquire()
                                                                if final:
                                                                        # EntryCount['positive'] += 1
                                                                        WordCount[sequence[index][0]]['positive'] += 1
                                                                        if EntryCount.get(sequence[index][0], 0):
                                                                                if final != self.flag:
                                                                                        EntryCount[sequence[index][0]]['positive'] += 1
                                                                                        EntryCount[sequence[index][0]]['negative'] -= 1
                                                                        else:
                                                                                EntryCount[sequence[index][0]]['positive'] = self.Ptotal
                                                                                EntryCount[sequence[index][0]]['negative'] = self.Ntotal
                                                                                if final != self.flag:
                                                                                        EntryCount[sequence[index][0]]['positive'] += 1
                                                                                        EntryCount[sequence[index][0]]['negative'] -= 1
                                                                else:
                                                                        # EntryCount['negative'] += 1
                                                                        WordCount[sequence[index][0]]['negative'] += 1
                                                                        if EntryCount.get(sequence[index][0], 0):
                                                                                if final != self.flag:
                                                                                        EntryCount[sequence[index][0]]['positive'] -= 1
                                                                                        EntryCount[sequence[index][0]]['negative'] += 1
                                                                        else:
                                                                                EntryCount[sequence[index][0]]['positive'] = self.Ptotal
                                                                                EntryCount[sequence[index][0]]['negative'] = self.Ntotal
                                                                                if final != self.flag:
                                                                                        EntryCount[sequence[index][0]]['positive'] -= 1
                                                                                        EntryCount[sequence[index][0]]['negative'] += 1
                                                                # word_set.add(sequence[index][0])
                                                                threadLock.release()
                        threadLock.acquire()
                        line = self.fp.readline()
                        threadLock.release()

def CountIP(ptree):
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
                        if child.label() != 'PU':
                                count += 1
                return count
        balance = len(ParentGroup)
        balanceTotal = balance
        tempList = []
        for x in range(0, len(ParentGroup)):
                tempTree = ParentGroup.popleft()
                flagTree = 1
                balanceSub = 0
                for child in tempTree:
                        IPGroup.append(child)
                        balanceSub += 1
                        if child.label() != 'IP':
                                if child.label() != 'PU':
                                        count += 1
                                flagTree = 0
                        else:
                                count += 1
        return count
        #         if flagTree:
        #                 for child in tempTree:
        #                         for grandchild in child:
        #                                 if grandchild.label() != 'IP':
        #                                         balanceSub -= 1
        #                                         break
        #                 if balanceSub:
        #                         # print("SubTree Unbalance Case")
        #                         # print(ptree)
        #                         balance -= 1              
        # if balance == balanceTotal:
        #         return count
        # elif not balance:
        #         # print("SubTree Unbalance Tree balance")
        #         return count
        # else:
        #         # print("SubTree Unbalance Tree unbalance")
        #         return count

def PreScanning(fp):
        count = 0
        for lines in fp:
                line = lines[:-1]
                try:
                        ptree = ParentedTree.fromstring(line)
                except:
                        line = line.replace('(PU )','(PU ）')
                        line = line.replace('(PU (','(PU （')
                        ptree = ParentedTree.fromstring(line)
                else:
                        pass
                count += CountIP(ptree)
        return count

def CoutingIPNumber(pos_parser_file):
        with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
                TotalIPNumber = PreScanning(fp)
        return TotalIPNumber

def MiningFromText(flag, pos_parser_file, dp_parser_file, POSset, negator_set, EntryCount, WordCount, IPTotalNumber):
        thread_num = 20
        threads = []
        with open(pos_parser_file, 'r', encoding = 'utf-8') as fp:
                with open(dp_parser_file, 'r', encoding = 'utf-8') as fp2:
                        for x in range(0, thread_num):
                                name = 'Thread-{}'.format(x + 1)
                                thread = myThread(x + 1, name, x + 1, fp, fp2, flag, IPTotalNumber['positive'], IPTotalNumber['negative'])
                                thread.start()
                                threads.append(thread)

                        # 等待所有线程完成
                        for t in threads:
                                t.join()
                        print ("Exiting Main Thread")
                        # print(count)
                                
POSset = set()
EntryCount = defaultdict(Counter)
WordCount = defaultdict(Counter)
negator_set = set()
threadLock = threading.Lock()

def BuildingDiscourse_Multi(argv): 
        sys.setrecursionlimit(2000)   
        global POSset
        global EntryCount
        global WordCount
        global negator_set
        None_set = {"NR", "NT", "NN"}
        Verb_set = {"VA", "VC", "VE", "VV"}
        Advb_set = {"AD"}
        Adjc_set = {"JJ"}
        threshold = 10           # At least appears ten times
        POSset = Verb_set | Advb_set | Adjc_set
        polarization = {'positive','negative'}
        ParseResultAddress = './Entry_processed/Entry_fullparsing/'
        DPResultAddress = './Entry_processed/DP_Result/'
        # ParseResultAddress = './experiment/Entry_processed/Entry_fullparsing/'
        path = './negator.txt'
        ReadInNegator(negator_set, path)
        # mutex = multiprocessing.RLock()       # mutex lock of multi-threading
        prefix = 'FullPasingResult_Segmented_Entry_'
        dprefix = 'DPResult_Segmented_Entry_'
        IPTotalNumber = {}
        for polar in polarization:
                # pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
                # IPTotalNumber[polar] = CoutingIPNumber(pos_parser_file)
                # print(polar) 
                # print(IPTotalNumber[polar])
                if polar == 'positive':
                        IPTotalNumber[polar] = 409816
                else:
                        IPTotalNumber[polar] = 269869
        for polar in polarization:
                if polar == 'positive':
                        pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
                        dp_parser_file = DPResultAddress + dprefix + polar + '_training.txt'
                        MiningFromText(1, pos_parser_file, dp_parser_file, POSset, negator_set, EntryCount, WordCount, IPTotalNumber)
                else:               # Read in the negative file
                        pos_parser_file = ParseResultAddress + prefix + polar + '_training.txt'
                        dp_parser_file = DPResultAddress + dprefix + polar + '_training.txt'
                        MiningFromText(0, pos_parser_file, dp_parser_file, POSset, negator_set, EntryCount, WordCount, IPTotalNumber)
        package = []
        Calculation(package, threshold, EntryCount, WordCount, IPTotalNumber)
        OutputResult(package)


if __name__ == '__main__':
        BuildingDiscourse_Multi(sys.argv[1:])