0. 数据预处理
gen_db.py: 创建cve数据表，从nvd的数据中构建cve数据
gen_cwe_rel.py: 创建cwe_rel数据表，记录cwe之间的从属关系
1. 训练
train.py: 通过lightgbm来训练模型，分别对cve707、cve693、unique_cve来训练，并保存模型
predict_cwe.py： 通过cwe之间的关系，来预测每一种cwe的权重
2. 测试
test.py： 根据给定的数据来预测得分


1.模型解释
评估模型为：
    [PR,E,T,I]→Base,I=Max(CI,II,AI)
	Score = [Base*A*V, M(E,T)] * W

Base为基于[pr,cwe,vendor,impact]训练出来的lightGBM模型；M(E,T)为基于[cwe,vendor]的实际漏洞改造难度评估模型（Modify)。
W为两种模型所占的权重，根据现实需求，W取[0.7,0.3]，即Score = 0.7*Base+0.3*Modify。

2.数据处理
测试数据中没有[pr,impact]，默认以[None, High]来补足，所以最后的评分也是过高估计的。
excel中第一项漏洞类型为空指针引用(CWE-476)不在考虑范围内，目前只能给出baseScore，modifyScore以均值赋值。

3.运行
venv中已经包含了工程需要的python库，可以直接运行:
$ venv/Scripts/python test.py
[7.030901310224497, 7.882613991444016, 7.829200735959396, 7.829200735959396, 7.829200735959396, 7.829200735959396]
