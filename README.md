### 5. 下游任务测试和微调

#### 5.1. 命名实体识别

共有两种方式:

- 直接进行Fine-tuning
- 抽取feature作为word_embeddiing,送入LSTM+CRF

分别进行两种方式的测试,另外加入使用同样语料训练word2vec获得的词向量进行对比.

基于预训练的albert_tiny, 训练3个epoch, 在MSRA数据集上有了明显的下降:

```
eval_f = 0.64703953
eval_precision = 0.7583809
eval_recall = 0.59024256
global_step = 2374
loss = 62.947628
```

(这里说明科技文献语料与Wikipedia预料明显的差别)