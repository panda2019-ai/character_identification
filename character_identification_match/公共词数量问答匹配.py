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


def find_lcseque(s1, s2):
    # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
    m = [[0 for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]
    # d用来记录转移方向
    d = [[None for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]

    for p1 in range(len(s1)):
        for p2 in range(len(s2)):
            if s1[p1] == s2[p2]:  # 字符匹配成功，则该位置的值为左上方的值加1
                m[p1 + 1][p2 + 1] = m[p1][p2] + 1
                d[p1 + 1][p2 + 1] = 'ok'
            elif m[p1 + 1][p2] > m[p1][p2 + 1]:  # 左值大于上值，则该位置的值为左值，并标记回溯时的方向
                m[p1 + 1][p2 + 1] = m[p1 + 1][p2]
                d[p1 + 1][p2 + 1] = 'left'
            else:  # 上值大于左值，则该位置的值为上值，并标记方向up
                m[p1 + 1][p2 + 1] = m[p1][p2 + 1]
                d[p1 + 1][p2 + 1] = 'up'
    (p1, p2) = (len(s1), len(s2))
    s = []
    while m[p1][p2]:  # 不为None时
        c = d[p1][p2]
        if c == 'ok':  # 匹配成功，插入该字符，并向左上角找下一个
            s.append(s1[p1 - 1])
            p1 -= 1
            p2 -= 1
        if c == 'left':  # 根据标记，向左找下一个
            p2 -= 1
        if c == 'up':  # 根据标记，向上找下一个
            p1 -= 1
    s.reverse()
    return ''.join(s)


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
    outfile = open('公共词数量问答匹配_角色识别结果.txt', 'wb')
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
                    common_str = find_lcseque(p_utterance, p_pro_utterance)
                    if len(common_str) >= 1:
                        out_str = u'预测被@用户=%s ||| 公共子串比例=%.2f ||| 公共子串=%s ||| 内容=%s' % (pro_user_name, 
                            len(common_str)/ min(len(p_utterance), len(p_pro_utterance)), 
                            common_str, 
                            pro_utterance)
                        out_li.append(out_str)
                if len(out_li) > 1:
                    out_str = u'\n'.join(out_li)
                    out_str += u'\n\n'
                    outfile.write(out_str.encode('utf-8', 'ignore'))

    outfile.close()
