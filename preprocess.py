import os
import json

def split_by_journal(path, contents):
    journal_dict = {}
    
    with open(os.path.join(path,contents), 'r') as f:
        for i in f.readlines():
            data = json.loads(i.strip())
            if data['media_c'] not in journal_dict:
                journal_dict[data['media_c']] = [data['_keyid']]
                # "netfulltextaddr_all_std":"{'TONGFANG@CNKI':['JSJY201807033'],'WANFANG@WANFANGDATA':['jsjyy201807032']}"
            else:
                journal_dict[data['media_c']].append(data['_keyid'])
    f.close()
    path = os.path.join(path,'split')
    if not os.path.exists(path):
        os.mkdir(path)
    for i in journal_dict.keys():
        with open(os.path.join(path,i+'.txt'), 'w') as f:
            for j in journal_dict[i]:
                f.write(j + '\n')
        f.close()
    return [(i, len(journal_dict[i]))for i in journal_dict.keys()]

if __name__ == "__main__":
    info = split_by_journal('/Users/lvyufeng/Downloads/CS_Journal_2016-2018', 'total.txt')
    print(info)