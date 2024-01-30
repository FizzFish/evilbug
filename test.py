import joblib
from sklearn.preprocessing import OrdinalEncoder

import lightgbm as lgb
# 读取模型
bst, encoder, vendors = joblib.load('data/gbm.pkl')
# 可以使用训练好的模型进行预测
xml_data = [['476', 'nautilus'], ['77', 'tenda'], ['77', 'totolink'], ['77', 'totolink'], ['77', 'totolink'], ['77', 'totolink']]

def test_data(data):
    new_data = []
    for x in data:
        item = ['LOW']+x+['HIGH']
        # if item[2] not in vendors:
        #     item[2] = 'unknown'
        new_data.append(item)
    data_encoded = encoder.transform(new_data)
    new_pred = bst.predict(data_encoded)
    print(f'Prediction for new data: {new_pred}')

test_data(xml_data)