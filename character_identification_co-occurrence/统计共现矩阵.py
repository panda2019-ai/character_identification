# coding:utf-8
"""
"""

import codecs
import json
from pyhanlp import *
import time
import numpy as np

Term =JClass("com.hankcs.hanlp.seg.common.Term")
NotionalTokenizer = JClass("com.hankcs.hanlp.tokenizer.NotionalTokenizer")


vocabulary_dict = dict()


# 加载词汇表
t0 = time.time()
vocabulary_dict = dict()
word_ser = 0
with codecs.open('data/vocabulary.txt', 'rb', 'utf-8', 'ignore') as infile:
    for line in infile:
        line = line.strip()
        if line:
            try:
                word, cnt = line.split()
            except:
                print(line)
                continue
            vocabulary_dict[word] = word_ser
            word_ser += 1
print("vocabulary len = ", len(vocabulary_dict))
t1 = time.time()
print("time: %.2f min" % ((t1 -t0)/60.0))


co_occurence_matrix = np.zeros((len(vocabulary_dict),len(vocabulary_dict)),dtype=np.int16)
print(co_occurence_matrix.shape)
print(co_occurence_matrix[0].shape)

t0 = time.time()
with codecs.open('data/baike_qa_valid.json', 'rb', 'utf-8', 'ignore') as infile:
    for line_ser, line in enumerate(infile):
        line_ser += 1
        print(line_ser, end=', ',flush=True)
        # if line_ser >= 100:
        #     break
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
                q_word_li = list([str(w.word) for w in NotionalTokenizer.segment(question) if str(w.nature) != u'nx' and len(str(w.word)) > 1])
                a_word_li = list([str(w.word) for w in NotionalTokenizer.segment(answer) if str(w.nature) != u'nx' and len(str(w.word)) > 1])
                # 遍历问题中的每个词
                for q_word in q_word_li:
                    # 如果该词在词典中则进行后续统计
                    if q_word in vocabulary_dict:
                        # 遍历回答中的每个词
                        for a_word in a_word_li:
                            # 如果该词在词典中则进行后续统计
                            if a_word in vocabulary_dict:
                                q_idx = vocabulary_dict[q_word]
                                a_idx = vocabulary_dict[a_word]
                                co_occurence_matrix[q_idx][a_idx] += 1

print("\n统计完毕")
t1 = time.time()
print("time: %.2f min" % ((t1 -t0)/60.0))

# t0 = time.time()
# vocabulary_matrix = np.array(list(vocabulary_dict.keys())).reshape(len(vocabulary_dict),1)
# out_matrix = np.hstack((vocabulary_matrix,co_occurence_matrix))
# print("组合词汇表和共现矩阵完毕")
# t1 = time.time()
# print("time: %.2f min" % ((t1 -t0)/60.0))

t0 = time.time()
np.save("data/co-occurence", co_occurence_matrix)
# np.savetxt("data/co-occurence.txt", co_occurence_matrix, fmt='%d')
print("输出到文件完毕")
t1 = time.time()
print("time: %.2f min" % ((t1 -t0)/60.0))
