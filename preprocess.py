import os
import json
from utils.mysql_conn import *
import argparse
import threading
import time

def get_area_data(conn, year, cn_class):
    sql = "select * from `{}` where Remark_C is not null and Class like \"%{}%\"".format(year, cn_class)
    data = fetch_data(conn, sql)
    return data

def get_data_by_year(conn, year):
    sql = "select * from `{}` where Remark_C is not null".format(year)
    data = fetch_data(conn, sql)
    return data

def write_txt(processed_data, path):
    max_len = 0
    long_text = 0
    with open(path, 'w', encoding='utf-8') as f:
        for article in processed_data:
            for sentence in article:
                f.write(sentence+'\n')
                if len(sentence) > max_len:
                    max_len = len(sentence)
                if len(sentence) > 512:
                    long_text += 1
                    # print(sentence)
                    continue
            f.write('\n')
    f.close()
    print('sent_max_len:{}'.format(max_len),long_text)
def process_txt(raw_data):
    # i[12] 'Remark_C'
    processed_data = []
    for i in raw_data:
        abstract = i[12]
        if '。' in i[12]:
            abstract = abstract.split('。')
            if '' in abstract:
                abstract.remove('')
        if '．' in i[12]: #．
            if type(abstract) == list:
                abstract = abstract[0]
            abstract = abstract.split('．')
            if '' in abstract:
                abstract.remove('')
        if '.' in i[12]:
            if type(abstract) == list:
                abstract = abstract[0]
            abstract = abstract.split('.')
            tmp = []
            for i in abstract:
                if i == '':
                    continue
                if i[0].isdigit() and tmp:
                    tmp[-1] = tmp[-1] + '.' + i
                else:
                    tmp.append(i)
            abstract = tmp
        if type(abstract) == list:
            abstract = [i + '。' for i in abstract]
            processed_data.append(abstract)
        else:
            processed_data.append([abstract])
    return processed_data

def main(conn, year, cn_class, data):
    cs_data = get_area_data(conn,year,'TP3')
    processed_data = process_txt(cs_data)
    data.extend(processed_data)
    print('{}:{}'.format(year, len(cs_data)))
    # sent_num = write_txt(processed_data,path)
    # print('article_num:{}, sent_num:{}'.format(len(cs_data),sent_num))

if __name__ == "__main__":
    # years = [2019]
    years = [i for i in range(2000,2020)]
    threads = []
    data = []
    for i in years:
        conn = connect('202.202.5.140',3306, 'root','cqu1701','cqvip') 
        thread = threading.Thread(target=main, args=(conn,i,'TP3',data,))
        threads.append(thread)
    for i in threads:
        i.setDaemon(True)
        i.start()
    i.join()
    time.sleep(5)
    print('article_num:{}, sent_num:{}'.format(len(data), sum([len(i) for i in data])))
    write_txt(data,'./cs_raw.txt')