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
        # 识别"@用户名"
        mention_username_li = match_pattern(utterance, u'@[^\s，。!]+')

        # 识别第2人称代词，你
        mention_pronoun_li = match_pattern(utterance, u'你', u'你们')
        
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

        # 统计含有"@用户名"的发言数
        # if mention_username_li:
        #     cnt += 1

        if mention_username_li and mention_pronoun_li:
            # 统计含有"@用户名"且含有"你"的发言数
            # cnt += 1
            if repeat_question_pattern:        # 反复疑问句
                cnt += 1 # 统计含有"@用户名"且含有"你"且为疑问句的发言数
                print('反复', repeat_question_pattern, utterance)
            elif alternative_question_pattern: # 选择疑问句
                cnt += 1 # 统计含有"@用户名"且含有"你"且为疑问句的发言数
                print('选择', alternative_question_pattern, utterance)
            elif particular_question_pattern:  # 特指疑问句
                cnt += 1 # 统计含有"@用户名"且含有"你"且为疑问句的发言数
                print('特指', particular_question_pattern, utterance)
            elif whether_question_pattern:    # 是非疑问句
                cnt += 1 # 统计含有"@用户名"且含有"你"且为疑问句的发言数
                print('是非', whether_question_pattern, utterance)
            else:
                continue
    print("cnt=", cnt)

