import re
from collections import defaultdict

def extract_item(tag, tokens, it, continuous=False):
        item = []
        text = ''
        for i in range(it, len(tokens)):
                text += tokens[i]
                if tag.startswith(text):
                        item.append('{}'.format(i))
                        if tag == text:
                                return i, item
                        elif not continuous:
                                break
                else:
                        break
        return it, None

class LinkageDetector(object):

        def __init__(self, tag_path):
                """Creates likage detector by connective token file"""
                with open(tag_path, 'r', encoding = 'utf-8') as f:
                        linker = {}
                        for l in f:
                                temp = defaultdict(float)
                                arg1, arg2, count, temp['a'], temp['b'], temp['c'], temp['d'] = l.rstrip().split(',')
                                if temp['c'] == max(temp.values()):
                                        linker[(arg1, arg2)] = float(temp['c']) * float(count)
                        self.tags = linker  # Tuple set

        def detect_by_tokens(self, tokens, *, continuous=False, cross=False):
                for tag in self.tags:
                        for indices in self.extract_tag(0, tag, 0, tokens,
                                                                                        continuous=continuous,
                                                                                        cross=cross):
                                yield tag, indices, self.tags[tag]
##
## Parameters after “*” or “*identifier” are keyword-only parameters 
## and may only be passed used keyword arguments.
##
        def extract_tag(self, idx, tag, it, tokens, *,
                                        items=None, continuous=False, cross=False):
                """
                continuous: include continuous tokens
                cross: must cross boundary
                """
                if items is None:
                        items = []

                if idx >= len(tag):
                        yield tuple(','.join(item) for item in items)
                else:
                        if not tag[idx]:
                                item = []
                                if not idx:
                                        item.append('{}'.format(it))
                                else:
                                        item.append('{}'.format(len(tokens)))
                                items.append(item)
                                yield from self.extract_tag(
                                        idx + 1, tag, it, tokens,
                                        items=items, continuous=continuous)
                                items.pop()
                        else:    
                                for i in range(it, len(tokens)):
                                        offset, item = extract_item(
                                                tag[idx], tokens, i, continuous)
                                        if item is not None:
                                                items.append(item)
                                                if cross:
                                                        while offset < len(tokens):
                                                                if re.search(r'\W', tokens[offset]) is not None:
                                                                        break
                                                                else:
                                                                        offset += 1
                                                yield from self.extract_tag(
                                                        idx + 1, tag, offset + 1, tokens,
                                                        items=items, continuous=continuous)
                                                items.pop()