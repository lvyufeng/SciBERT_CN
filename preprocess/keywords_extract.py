import os
from utils.mysql_conn import *
import threading
import argparse
import time
def get_area_keywords(conn, year, cn_class):
    sql = "select KeyWord_C from `{}` where KeyWord_C is not null and Title_E != \"\" and Class like \"%{}%\"".format(year, cn_class)
    data = fetch_data(conn, sql)
    # print(len(data))
    return data
def process_txt(data):
    keywords = []
    for i in data:
        if ' ' in i[0]:
            keys = i[0].split(' ')
        elif ';' in i[0]:
            keys = i[0].split(';')
        keywords.extend(keys)
    return list(set(keywords))

def process_data(conn, year, cn_class, keywords):
    cs_data = get_area_keywords(conn,year,'TP3')
    # print(len(cs_data))
    
    processed_data = process_txt(cs_data)
    
    keywords.extend(processed_data)
    print('{}:{}'.format(year, len(cs_data)))

def write_txt(processed_data, path):
    processed_data = list(set(processed_data))
    with open(path, 'w', encoding='utf-8') as f:
        for i in processed_data:
            f.write(i+'\n')
    f.close()

def main(args):
    years = [i for i in range(2000,2020)]
    threads = []
    keywords = []
    for i in years:
        conn = connect(args.ip,args.port, args.user,args.passwd,args.db) 
        thread = threading.Thread(target=process_data, args=(conn,i,'TP3',keywords,))
        threads.append(thread)
    for i in threads:
        i.setDaemon(True)
        i.start()
    i.join()
    # time.sleep(5)
    print('keywords num:{}'.format(len(keywords)))
    write_txt(keywords,os.path.join(args.path,'keywords.txt'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect mysql and extract data')
    parser.add_argument('--ip',default='localhost')
    parser.add_argument('--port', default=3306)
    parser.add_argument('--user',default='root')
    parser.add_argument('--passwd', default='passwd')
    parser.add_argument('--db', default='db')
    parser.add_argument('--path',default='./')
    args = parser.parse_args()
    main(args)