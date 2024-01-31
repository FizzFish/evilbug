import json
import joblib

# 从excel中提取数据
xml_data = [['476', 'nautilus'], ['77', 'tenda'], ['77', 'totolink'], ['77', 'totolink'], ['77', 'totolink'],
            ['77', 'totolink']]


def base_score(test_data):
    # 读取模型
    bst, encoder, vendors = joblib.load('data/gbm.pkl')
    new_data = []
    for x in test_data:
        # 以{pr: NONE, impact: HIGH}做数据补足
        item = ['NONE'] + x + ['HIGH']
        # if item[2] not in vendors:
        #     item[2] = 'unknown'
        new_data.append(item)
    data_encoded = encoder.transform(new_data)
    new_pred = bst.predict(data_encoded)
    # print(f'gbm: {new_pred}')
    return new_pred


def modify_score(test_data):
    with open("data/cwe_value707.json", "r") as json_file:
        values = json.load(json_file)
    new_data = []
    for entry in test_data:
        cwe = entry[0]
        if cwe in values.keys():
            new_data.append(values[cwe])
        else:
            new_data.append(values['avg'])
    return new_data


def eval_cve(test_data):
    size = len(test_data)
    base = base_score(test_data)
    modify = modify_score(test_data)
    return [base[i] * 0.7 + modify[i] * 0.3 for i in range(size)]


scores = eval_cve(xml_data)
print(scores)
