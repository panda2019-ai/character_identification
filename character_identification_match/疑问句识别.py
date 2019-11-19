# coding:utf-8
"""
识别疑问句，分为4类，分别为
1. 反复疑问句
2. 选择疑问句
3. 特指疑问句
4. 是非疑问句
"""

import re
import codecs


# 模式匹配，返回匹配的串
def match_pattern(utterance, regex_exp, not_regex_exp=u''):
    mention = u''
    # 去掉邮箱地址
    utterance = re.sub(u'[a-zA-Z0-9]+@[a-zA-Z0-9.]+', u'', utterance)
    # 去掉程序语言关键词
    utterance = re.sub(u'@array', u'', utterance)

    # 不匹配的模式
    if not_regex_exp and re.search(not_regex_exp, utterance):
        return []

    m = re.search(regex_exp, utterance)
    if m:
        mention = m.group(0)

    return mention


# 是否匹配"@用户名"和第2人称代词"你"
def match_mention(utterance):
    mention_username_li, mention_pronoun_li = None, None
    # 识别"@用户名"
    mention_username_li = match_pattern(utterance, u'@[^\s，。!]+')
    # 识别第2人称代词，你
    mention_pronoun_li = match_pattern(utterance, u'你', u'你们')
    # 发言中含有“@用户名”并且含有第2人称代词“你”
    return mention_username_li, mention_pronoun_li


# 匹配问题类型
def match_question_class(utterance):
    # 匹配反复疑问句
    repeat_question_pattern = match_pattern(utterance, u'(\w)不\\1')
    repeat_question_pattern += match_pattern(utterance, u'(\w)没\\1')

    # 匹配选择疑问句
    alternative_question_pattern = match_pattern(utterance, u'还是[^,，?？]+[?？]')

    # 匹配特指疑问句
    particular_question_pattern = match_pattern(utterance, u'谁[^,，?？]*[?？]')
    particular_question_pattern += match_pattern(utterance, u'什么[^,，?？]*[?？]')
    particular_question_pattern += match_pattern(utterance, u'哪[^,，?？]*[?？]')
    particular_question_pattern += match_pattern(utterance, u'多少[^,，?？]*[?？]')
    particular_question_pattern += match_pattern(utterance, u'怎么样[^,，?？]*[?？]')
    particular_question_pattern += match_pattern(utterance, u'啥[^,，?？]*[?？]')

    # 匹配是非疑问句
    whether_question_pattern = match_pattern(utterance, u'\?|\？')

    if repeat_question_pattern:        # 反复疑问句
        return ('反复', repeat_question_pattern)
    elif alternative_question_pattern: # 选择疑问句
        return ('选择', alternative_question_pattern)
    elif particular_question_pattern:  # 特指疑问句
        return ('特指', particular_question_pattern)
    elif whether_question_pattern:    # 是非疑问句
        return ('是非', whether_question_pattern)
    else:
        return None

# 
if __name__ == "__main__":
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
    print("发言总数=", len(utterance_li))
    
    # 遍历发言
    cnt = 0
    for utterance_ser, (user_name, utterance) in enumerate(utterance_li):
            if match_mention(utterance):
                # 匹配问题类型
                question_info = match_question_class(utterance)
                if question_info:
                    question_class, question_pattern = question_info
                    print(question_class, question_pattern, utterance)
