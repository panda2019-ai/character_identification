# coding:utf-8
"""
基于公共词数量的问答匹配，
进而完成角色识别
"""

from 疑问句识别 import match_question_class
from 疑问句识别 import match_mention
import codecs
from pyhanlp import *
NotionalTokenizer = JClass("com.hankcs.hanlp.tokenizer.NotionalTokenizer")
import re
import time
import numpy as np

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

# 加载共现矩阵
co_occurence_matrix = np.load("data/co-occurence.npy")
print("co-occurence matrix shape = ", co_occurence_matrix.shape)


def compute_correlation(question, answer):
    q_word_li = list([str(w.word) for w in NotionalTokenizer.segment(question)])
    a_word_li = list([str(w.word) for w in NotionalTokenizer.segment(answer) ])
    
    D_li = []
    for q_word in q_word_li:
        d_li = []
        if q_word in vocabulary_dict:
            for a_word in a_word_li:
                if a_word in vocabulary_dict:
                    q_idx = vocabulary_dict[q_word]
                    a_idx = vocabulary_dict[a_word]
                    if co_occurence_matrix[q_idx][a_idx] > 0:
                        d_li.append(co_occurence_matrix[q_idx][a_idx])
        if d_li:
            d_array = np.array(d_li, dtype=np.int32)
            dia = np.sqrt(np.dot(d_array,d_array))/len(d_li)
            # print(d_li)
            # print("d_array.dtype= ", d_array.dtype)
            # print("d_array.shape=", d_array.shape)
            # print("np.dot=", np.dot(d_array,d_array))
            # print("dia=", dia)
            D_li.append(dia)
    if D_li:
        return sum(D_li)/len(D_li)
    else:
        return 0


# 获取发言后续的非发言者的发言5句
def get_pro_utterance(utterance_li, cur_user_name, cur_utterance_ser, max_cnt=5):
    pro_utterance_li = []
    for pro_user_name, pro_utterance in utterance_li[cur_utterance_ser+1:]:
        if pro_user_name != cur_user_name:
            pro_utterance_li.append((pro_user_name, pro_utterance))
            if len(pro_utterance_li) >= max_cnt:
                break
    return pro_utterance_li


# 预处理
def preprocess(text):
    text = re.sub(u'\[图片\]', u'', text)
    text = re.sub(u'\[表情\]', u'', text)
    text = re.sub(u'你好', u'', text)
    text = re.sub(u'@[^\s，。!]+', u'', text)
    text = re.sub(u'@', u'', text)
    word_li = list(NotionalTokenizer.segment(text))
    return u''.join([w.word for w in word_li])


if __name__ == '__main__':
    outfile = open('词共现矩阵问答匹配_角色识别结果.txt', 'wb')
    # 读取所有发言
    utterance_li = []
    with codecs.open('data/qqdata.txt', 'rb', 'utf-8', 'ignore') as infile:
        for line in infile:
            line = line.strip()
            if line:
                items_li = line.split(u'\t')
                if len(items_li) != 3:
                    continue
                else:
                    user_id, user_name, utterance = items_li
                    utterance_li.append((user_name, utterance))

    # 遍历发言
    for utterance_ser, (user_name, utterance) in enumerate(utterance_li):
        # 发言含有"@用户名"和第2人称代词"你"
        mention_username_li, mention_pronoun_li = match_mention(utterance)
        if mention_username_li and mention_pronoun_li:
            # 匹配问题类型
            question_info = match_question_class(utterance)
            # 发言为问句
            if question_info:
                out_li = []
                # 提取发言后续5条发言
                pro_utterance_li = get_pro_utterance(utterance_li, user_name, utterance_ser)
                # 遍历发言后续5条发言
                out_str = u'被@用户=%s ||| 发言者=%s ||| 内容=%s' % (u' '.join(mention_username_li), user_name, utterance)
                out_li.append(out_str)
                for pro_user_name, pro_utterance in pro_utterance_li:
                    p_utterance = preprocess(utterance)
                    p_pro_utterance = preprocess(pro_utterance)
                    cor = compute_correlation(p_utterance, p_pro_utterance)
                    if cor > 0:
                        out_str = u'预测被@用户=%s ||| 相关度=%.2f ||| 内容=%s' % (pro_user_name, 
                            cor, pro_utterance)
                        out_li.append(out_str)
                if len(out_li) > 1:
                    out_str = u'\n'.join(out_li)
                    out_str += u'\n\n'
                    outfile.write(out_str.encode('utf-8', 'ignore'))

    outfile.close()
