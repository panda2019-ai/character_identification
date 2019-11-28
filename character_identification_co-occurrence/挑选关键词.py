# coding:utf-8
"""
"""

import codecs
import json
from pyhanlp import *
import time

Term =JClass("com.hankcs.hanlp.seg.common.Term")
NotionalTokenizer = JClass("com.hankcs.hanlp.tokenizer.NotionalTokenizer")


vocabulary_dict = dict()

t0 = time.time()

with codecs.open('data/baike_qa_valid.json', 'rb', 'utf-8', 'ignore') as infile:
    for line in infile:
        line = line.strip()
        if line:
            try:
                json_dict = json.loads(line)
                category = json_dict['category'].strip()
                question = json_dict['desc'].strip()
                answer = json_dict['answer'].strip()
            except:
                continue
            if category and question and answer:
                q_word_li = list([w.word for w in NotionalTokenizer.segment(question) if str(w.nature) != u'nx' and len(str(w.word)) > 1])
                a_word_li = list([w.word for w in NotionalTokenizer.segment(answer) if str(w.nature) != u'nx' and len(str(w.word)) > 1])
                for word in q_word_li:
                    if word not in vocabulary_dict:
                        vocabulary_dict[word] = 1
                    else:
                        vocabulary_dict[word] += 1
                for word in a_word_li:
                    if word not in vocabulary_dict:
                        vocabulary_dict[word] = 1
                    else:
                        vocabulary_dict[word] += 1


with open('data/vocabulary.txt', 'wb') as outfile:
    for word, cnt in vocabulary_dict.items():
        out_str = u'%s\t%d\n' % (word, cnt)
        outfile.write(out_str.encode('utf-8', 'ignore'))

t1 = time.time()
print("time: %.2f min" % ((t1 -t0)/60.0))
