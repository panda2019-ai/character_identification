# coding:utf-8
"""
角色识别
1. 识别“@用户名”mention
2. 判别疑问句
"""

import codecs 
import re
from pyhanlp import *
from nltk import ngrams
from demo_predict_is_next_sentence import is_next_sentence


question_grams1_set = set()
question_grams2_set = set()
question_grams3_set = set()

# 读取疑问句识别grams词表
def load_question_dictionary(file_path_name):
    global question_grams1_set
    global question_grams2_set
    global question_grams3_set

    with codecs.open(file_path_name, 'rb', 'utf-8', 'ignore') as infile:
        for line in infile:
            line = line.strip()
            if line:
                grams_li = line.split(u'_')
                if len(grams_li) == 1:
                    question_grams1_set.add(line)
                elif len(grams_li) == 2:
                    question_grams2_set.add(line)
                elif len(grams_li) == 3:
                    question_grams3_set.add(line)
                else:
                    pass
    print("len question_grams1_set = %d" % len(question_grams1_set))
    print("len question_grams2_set = %d" % len(question_grams2_set))
    print("len question_grams3_set = %d" % len(question_grams3_set))


# 识别mention
def identify_mention(utterance, regex_exp):
    mention_li = []
    # 去掉邮箱地址
    utterance = re.sub(u'[a-zA-Z0-9]+@[a-zA-Z0-9.]+', u'', utterance)
    # 去掉程序语言关键词
    utterance = re.sub(u'@array', u'', utterance)

    match_li = re.findall(regex_exp, utterance)
    if match_li:
        mention_li = match_li
    return mention_li

# 疑问句识别
def is_question_sentence(utterance):
    global question_grams1_set
    global question_grams2_set
    global question_grams3_set

    question_flag = False
    # 分词
    word_pos_li = list(HanLP.segment(utterance))
    word_li = [w.word for w in word_pos_li] 

    # 空句子返回假
    if not word_li:
        return False

    # 添加句子开始标志和句子阶数标志
    word_li.insert(0, 'start')
    word_li.append('stop')

    # 抽取2grams序列
    grams2_li = [u'_'.join(w) for w in ngrams(word_li, 2)]

    # 抽取3grams序列
    grams3_li = [u'_'.join(w) for w in ngrams(word_li, 3)]

    
    for w in word_li:
        if w in question_grams1_set:
            question_flag = True
            break

    for w in grams2_li:
        if w in question_grams2_set:
            question_flag = True
            break

    for w in grams3_li:
        if w in question_grams3_set:
            question_flag = True
            break
    
    return question_flag


if __name__ == "__main__":

    # 加载资源
    load_question_dictionary('data/疑问句标志词/question_ngrams.txt')

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

    outfile = open('待角色识别句子.txt', 'wb')

    # 遍历发言
    for utterance_ser, (user_name, utterance) in enumerate(utterance_li):
        # 识别"@用户名"
        mention_username_li = identify_mention(utterance, u'@[^\s，。!]+')
        # 识别第2人称代词，你/你们
        mention_pronoun_li = identify_mention(utterance, u'[你]')
        # 是否为疑问句
        is_question_flag = is_question_sentence(utterance)

        if is_question_flag and mention_username_li and mention_pronoun_li:

            print("user_name=", user_name, "utterance=", utterance)
            pro_utterance_li = utterance_li[utterance_ser+1: utterance_ser+1+5]
            for pro_user_name, pro_utterance in pro_utterance_li:
                print(is_next_sentence(utterance, pro_utterance), "pro_user_name=", pro_user_name, "pro_utterance=", pro_utterance)
            print()
    
    outfile.close()

