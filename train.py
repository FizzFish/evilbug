import sqlite3

import joblib
from sklearn.preprocessing import OrdinalEncoder

import lightgbm as lgb
import numpy as np
from sklearn.model_selection import train_test_split


def from_sql(db_name, table_name):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_name)  # 替换为你的数据库文件路径
    # 从数据库中获取数据
    query = "SELECT pr, cwe, vendor, impact, score FROM {}".format(table_name)
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    # # 自定义排序函数
    # def custom_sort(element):
    #     # 将第3维数据为 "unknown" 的元素排在最前面
    #     return (element[2] != 'unknown', element[2])
    #
    # # 使用 sorted 进行排序
    # sorted_data = sorted(data, key=custom_sort)
    vendors = set([x[2] for x in data])
    return conn, data, vendors


def train_data(db_data):
    # 将数据转换为 NumPy 数组
    data_array = np.array(db_data)
    # 分割特征和标签
    X = data_array[:, :-1]  # 特征
    y = data_array[:, -1].astype(float)  # 标签
    # 编码
    encoder = OrdinalEncoder()
    X_enc = encoder.fit_transform(X)
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X_enc, y, test_size=0.2, random_state=42)

    # 创建 LightGBM 数据集
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    # 设置 LightGBM 参数
    params = {
        'objective': 'regression',  # 回归问题
        'metric': 'l2',  # 平方损失
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.1,
        'feature_fraction': 0.9,
    }

    # 训练 LightGBM 模型
    num_round = 1000  # 迭代次数
    bst = lgb.train(params, train_data, valid_sets=[train_data, test_data], num_boost_round=1000,
                    callbacks=[lgb.early_stopping(stopping_rounds=50)])
    return encoder, bst


def save_model(encoder, bst, vendors, file_name):
    joblib.dump((bst, encoder, vendors), file_name)


def test(encoder, bst, conn, table_name):
    # 可以使用训练好的模型进行预测
    cursor = conn.cursor()
    query = "SELECT pr, cwe, vendor, impact, score FROM {} limit 5".format(table_name)
    cursor.execute(query)
    data = cursor.fetchall()
    data_X = [x[:-1] for x in data]
    data_y = [x[-1] for x in data]
    new_data_encoded = encoder.transform(data_X)
    new_pred = bst.predict(new_data_encoded)
    print(f'Value for data in db   : {data_y}')
    print(f'Prediction for new data: {new_pred}')


def close_db(conn):
    # 关闭数据库连接
    conn.close()

db_name='data/cve.db'
def train_from_table(table_name, file_name):
    conn, db_data, vendors = from_sql(db_name, table_name)
    encoder, bst = train_data(db_data)
    test(encoder, bst, conn, table_name)
    save_model(encoder, bst, vendors, file_name)
    close_db(conn)


# train_from_table('cve707', 'data/gbm707.pkl')
train_from_table('cve693', 'data/gbm693.pkl')
train_from_table('unique_cve', 'data/gbm.pkl')
