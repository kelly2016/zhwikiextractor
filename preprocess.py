# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 18:31
# @Author  : Kelly
# @Email   : 289786098@qq.com
# @File    : preprocess.py
# @Description:维基百科中文预处理:1,正则->繁体专简体->分词

from zhtools.langconv import *
import logging, jieba, os, re

PUNCTUATION_PATTERN = r'\”|\《|\。|\{|\！|？|｡|\＂|＃|＄|％|\＆|\＇|（|）|＊|＋|，|－|／|：|；|＜|＝|＞|＠|\［|\＼|\］|\＾|＿|｀|\～|｟|｠|\、|〃|》|「|」|『|』|【|】|〔|〕|〖|〗|〘|〙|〚|〛|〜|\〝|\〞|〟|〰|〾|〿|–—|\‘|\“|\„|\‟|\…|\‧|﹏|\.'
program = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(program)

def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


def punctuation(ustring):
    return re.sub(PUNCTUATION_PATTERN, '', ustring)


def get_stopwords(stopwordsFile = "../stop_words/stopwords.txt"):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
    # 加载停用词表
    stopword_set = set()
    if(os.path.exists(stopwordsFile)):
        with open(stopwordsFile, 'r', encoding="utf-8") as stopwords:
            for stopword in stopwords:
                stopword_set.add(stopword.strip("\n"))

    return stopword_set



def parse_zhwiki(read_file_path, save_file_path,stopwordsFile):
    """
    使用正则表达式解析文本
    :param read_file_path:
    :param save_file_path:
    :return:
    """
    # 过滤掉<doc>
    regex_str = "[^<doc.*>$]|[^</doc>$]"
    file = open(read_file_path, "r", encoding="utf-8")
    # 写文件
    output = open(save_file_path, "w+", encoding="utf-8")
    content_line = file.readline()
    # 获取停用词表
    stopwords = get_stopwords(stopwordsFile)
    # 定义一个字符串变量，表示一篇文章的分词结果
    article_contents = ""
    index = 0
    index2 = 0
    while content_line:
        match_obj = re.match(regex_str, content_line)
        content_line = content_line.strip("\n")
        #繁体专简体
        content_line =Traditional2Simplified(content_line)
        content_line = punctuation(content_line)
        if len(content_line) > 0:
            if match_obj:
                # 使用jieba进行分词
                words = jieba.cut(content_line, cut_all=False)
                for word in words:
                    if word not in stopwords:
                        article_contents += word + " "
            else:
                if len(article_contents) > 0:
                    output.write(article_contents + "\n")
                    index2 += 1
                    article_contents = ""
                    print("\033[0;30;40m\t line {} is writen \033[0m".format(index2))
        index += 1
        print("line {} is finished : {}".format(index,content_line))
        content_line = file.readline()
    output.close()




def generate_corpus(zhwiki_path,save_path,N,stopwordsFile):
    """
    将维基百科语料库进行分类
    :param zhwiki_path:
    :param save_path:
    :param N: 文件索引
    :return:
    """

    for i in range(N):
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
        file_path = os.path.join(zhwiki_path, str("wiki_0%s" % str(i)))
        parse_zhwiki(file_path, os.path.join(save_path, "zh_wiki_corpus0%s" % str(i)),stopwordsFile)
        logger.info("running save ", os.path.join(save_path, "zh_wiki_corpus0%s" % str(i))," successfully !")


def merge_corpus(inputDir,outputdir):
    """
    合并分词后的文件
    :param inputDir:
    :param outputdir:
    :return:
    """

    output = open( os.path.join(outputdir,"wiki_corpus"),"w",encoding="utf-8")

    for i in range(3):
        file_path = os.path.join(inputDir,str("zh_wiki_corpus0%s"%str(i)))
        file = open(file_path,"r",encoding="utf-8")
        line = file.readline()
        while line:
            output.writelines(line)
            line = file.readline()
        file.close()
    output.close()

if __name__ == '__main__':
    regex_str = "[^<doc.*>$]"
    match_obj = re.match(regex_str, '<doc id=/"988340/" url=/"https://zh.wikipedia.org/wiki?curid=988340/" title=/"白花八角/">')


    #traditional_sentence = '憂郁的臺灣烏龜'
    #simplified_sentence = Traditional2Simplified(traditional_sentence)
    #print(simplified_sentence)
    zhwiki_path = os.path.dirname(os.path.abspath(__file__))+ os.sep + 'zhwiki'+ os.sep + 'AA'
    save_path = os.path.dirname(os.path.abspath(__file__))+ os.sep + 'zhwiki'
    stopwordsFile = os.path.dirname(os.path.abspath(__file__))+ os.sep +'stopwords.txt'
    #解析整合
    generate_corpus(zhwiki_path, save_path, 3,stopwordsFile)
    #合并文件为一个
    merge_corpus(zhwiki_path, save_path)