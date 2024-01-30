import numpy as np
from scipy.optimize import minimize
import re

# 已知的节点对
node_pairs = []  # 举例
nodes = []
known_nodes = {707: 2, 20: 3, 917: 5}

def get_cp(file_name):
    with open(file_name, 'r') as fd:
        input_string = fd.read()
    # 使用正则表达式提取所有数字
    numbers = re.findall(r'\d+$', input_string, flags=re.MULTILINE)
    # 将提取的数字转换为集合，以获取不同的数字
    unique_numbers = set(numbers)
    # 输出结果
    for number in unique_numbers:
        nodes.append(int(number))

    # 定义正则表达式模式
    pattern = re.compile(r'\d+ > \d+$', flags=re.MULTILINE)
    # 使用findall()方法提取所有匹配的模式
    matches = pattern.findall(input_string)

    # 遍历所有匹配的模式
    for match in matches:
        nums = match.split(' > ')
        if nums[0] != '1000':
            x, y = int(nums[0]), int(nums[1])
            xi = nodes.index(x)
            yi = nodes.index(y)
            node_pairs.append((xi, yi))
    return node_pairs


# 构建联系矩阵
def build_correlation_matrix(node_pairs):
    correlation_matrix = np.zeros((len(nodes), len(nodes)))
    for pair in node_pairs:
        correlation_matrix[pair[0], pair[1]] = correlation_matrix[pair[1], pair[0]] = 1
    return correlation_matrix


# 定义已知的损失函数
def loss_function(x):
    return np.sum(np.where(correlation_matrix == 1, (x[:, np.newaxis] - x) ** 2, 0))


# 约束条件
def constraint_function(x):
    # 假设某些维度的值是已知的
    res = 0
    for k, v in known_nodes.items():
        i = nodes.index(k)
        res += ((x[i] - v) ** 2)
    return res


# 定义目标函数，包括已知的损失函数和约束条件
def objective_function(x):
    return loss_function(x) + constraint_function(x)


# 初始猜测值
get_cp('data/707')
initial_guess = np.zeros(len(nodes))

# 构建联系矩阵
correlation_matrix = build_correlation_matrix(node_pairs)
# 设置约束条件
constraints = {'type': 'eq', 'fun': constraint_function}

# 使用优化算法寻找使损失函数最小化的输入值
bounds = [(0, 5)] * len(nodes)
result = minimize(objective_function, initial_guess, constraints=constraints, bounds=bounds)

# 输出结果
optimized_input = result.x.astype(int)
for i, n in enumerate(nodes):
    print("{}:{}".format(n, optimized_input[i]))
