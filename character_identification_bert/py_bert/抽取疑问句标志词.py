# coding:utf-8
"""
从问答语料中抽取出疑问句标志词
"""

import codecs
import json
from pyhanlp import *
import sys


if len(sys.argv) != 3:
    print("抽取疑问句标志词.py inputfile_name, outputfile_name")
    exit(1)

inputfile_name = sys.argv[1]
outfile_name = sys.argv[2]



outfile = open(outfile_name, 'wb')

error_cnt = 0
with codecs.open(inputfile_name, 'rb', 'utf-8') as infile:
    for line_ser, line in enumerate(infile):
        line_ser += 1
        if line_ser % 1e+6 == 0:
            print(line_ser)
        line = line.strip()
        if line:
            try:
                json_dict = json.loads(line)
            except:
                error_cnt += 1
                print("error:", line)
                continue
            title = json_dict['title']
            # 分词
            word_pos_li = list(HanLP.segment(title))
            word_li = [w.word for w in word_pos_li] 
            # pos_li = [w.nature for w in word_pos_li]
            word_li_len = len(word_li)
            # 抽取各特征
            for word_ser, word in enumerate(word_li):
                # "x不y", "x没有y", "x没y"
                if 0 < word_ser < word_li_len-1 and word in [u'不', u'没有', u'没']:
                    out_str = u'%s_%s_%s\n' % (word_li[word_ser-1], word_li[word_ser], word_li[word_ser+1])
                    outfile.write(out_str.encode('utf-8', 'ignore'))
                
                if word in [u'谁', u'什么', u'哪儿', u'多少', u'怎么样']:
                    # "x谁", "x什么", "x哪儿", "x多少", "x怎么样"
                    if word_ser >0:
                        out_str = u'%s_%s\n' % (word_li[word_ser-1], word_li[word_ser])
                        outfile.write(out_str.encode('utf-8', 'ignore'))
                    
                    # "谁y", "什么y", "哪儿y", "多少y", "怎么样y"
                    if word_ser < word_li_len-1:
                        out_str = u'%s_%s\n' % (word_li[word_ser], word_li[word_ser+1])
                        outfile.write(out_str.encode('utf-8', 'ignore'))
                
                # "x还是y"
                if 0 < word_ser < word_li_len-1 and word == "还是":
                    out_str = u'%s_%s_%s\n' % (word_li[word_ser-1], word_li[word_ser], word_li[word_ser+1])
                    outfile.write(out_str.encode('utf-8', 'ignore'))

                # "x呢","x吗","x吧"
                if word_ser == word_li_len-1 and word in [u'吗', u'呢', u'吧']:
                    out_str = u'%s_%s\n' % (word_li[word_ser-1], word_li[word_ser])
                    outfile.write(out_str.encode('utf-8', 'ignore')) 


            
outfile.close()
print("error_cnt = %d" % error_cnt, flush=True)
print('finished', flush=True)
