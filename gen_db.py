import json
import sqlite3

import requests
from jsonpath import jsonpath
def get_vendor_from_net(cve_id):
    url = f"https://services.nvd.nist.gov/rest/json/cpematch/2.0?cveId={cve_id}"
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()
        cpes = jsonpath(json, '$..matchStrings..criteria')
        vendor = cpes[0].split(':')[3]
        return vendor
    return 'unknown'

def create_db(db_name):
    # 创建一个游标对象
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # 创建表格
    # ac,av,ai,ci,ii,pr,scope,ui
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS cve (
        id TEXT PRIMARY KEY,
        ac TEXT NOT NULL,
        av TEXT NOT NULL,
        ai TEXT NOT NULL,
        ci TEXT NOT NULL,
        ii TEXT NOT NULL,
        pr TEXT NOT NULL,
        ui TEXT NOT NULL,
        sco TEXT NOT NULL,
        vendor TEXT DEFAULT 'n/a',
        cwe TEXT NOT NULL,        
        score FLOAT DEFAULT 0
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()
    return conn

def extract_nvd(js_file):
    with open(js_file, 'r', encoding="utf-8", errors='ignore') as fd:
        cvelist = json.load(fd)["CVE_Items"]
    data_list = []
    for cveItem in cvelist:
        id = jsonpath(cveItem, '$..ID')[0]
        cwe_search = jsonpath(cveItem, '$..problemtype..value')
        cwe = cwe_search[0][4:] if cwe_search else 'Other'
        vendor_search = jsonpath(cveItem, '$..configurations..cpe23Uri')
        vendor = vendor_search[0].split(':')[3] if vendor_search else 'unknown'
        # descript = jsonpath(cveItem, '$..problemtype..value')
        if jsonpath(cveItem, '$..cvssV3'):
            score = jsonpath(cveItem, '$..cvssV3..baseScore')[0]
            ac = jsonpath(cveItem, '$..cvssV3..attackComplexity')[0]
            av = jsonpath(cveItem, '$..cvssV3..attackVector')[0]
            ai = jsonpath(cveItem, '$..cvssV3..availabilityImpact')[0]
            ci = jsonpath(cveItem, '$..cvssV3..confidentialityImpact')[0]
            ii = jsonpath(cveItem, '$..cvssV3..integrityImpact')[0]
            pr = jsonpath(cveItem, '$..cvssV3..privilegesRequired')[0]
            sco = jsonpath(cveItem, '$..cvssV3..scope')[0]
            ui = jsonpath(cveItem, '$..cvssV3..userInteraction')[0]
        elif jsonpath(cveItem, '$..cvssV2'):
            score = jsonpath(cveItem, '$..cvssV2..baseScore')[0]
            ac = jsonpath(cveItem, '$..cvssV2..accessComplexity')[0]
            av = jsonpath(cveItem, '$..cvssV2..accessVector')[0]
            ai = jsonpath(cveItem, '$..cvssV2..availabilityImpact')[0]
            ci = jsonpath(cveItem, '$..cvssV2..confidentialityImpact')[0]
            ii = jsonpath(cveItem, '$..cvssV2..integrityImpact')[0]
            pr = jsonpath(cveItem, '$..cvssV2..authentication')[0]
            sco = 'UNCHANGED'
            ui = 'NONE'
        else:
            continue

        data_list.append((id,ac,av,ai,ci,ii,pr,ui,sco,vendor,cwe,score))
    return data_list

def insert_data(data_list, conn):
    cursor = conn.cursor()
    # 插入数据 self.id,self.cveType,self.av,self.ac,self.pr,self.ui,self.scope,self.ci,self.ii,self.ai,self.score
    insert_data_query = '''
        INSERT OR REPLACE INTO cve (id,ac,av,ai,ci,ii,pr,ui,sco,vendor,cwe,score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
    cursor.executemany(insert_data_query, data_list)
    # 提交更改
    conn.commit()


conn = create_db('data/cve.db')
insert_data_query = '''
        INSERT OR REPLACE INTO cve (id,ac,av,ai,ci,ii,pr,ui,sco,vendor,cwe,score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
for year in range(2010, 2024):
    data_list = extract_nvd(f"nvd\\nvd{year}.json")
    # print(data_list[0])
    # conn.execute(insert_data_query, data_list[0])
    # conn.commit()
    # conn.close()
    insert_data(data_list, conn)
# 关闭连接
conn.close()