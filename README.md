# BERT-Chinese-CS
针对中文计算机科技文献的预训练模型(基于国图分类，筛选所有属于TP3的文献)。

由于项目需要（专业文本的自然语言处理），在维普提供海量科技文献文本，重庆市科学院提供算力支持的情况下，训练一个Domain Specific的预训练模型。

资源 | 统计 |
 -|-
 GPU | TeslaV100 x 3
期刊数| 943
文章数| 408187
句子数| 1243300

### 1. 数据准备

使用维普提供的2000-2019年全国核心期刊数据(仅摘要), 将文本分句后写入文件，格式如下：

```
卷积神经网络在单标签图像分类中表现出了良好的性能,但是,如何将其更好地应用到多标签图像分类仍然是一项重要的挑战。
本文提出一种基于卷积神经网络并融合注意力机制和语义关联性的多标签图像分类方法。
首先,利用卷积神经网络来提取特征;其次,利用注意力机制将数据集中的每个标签类别和输出特征图中的每个通道进行对应;最后,利用监督学习的方式学习通道之间的关联性,也就是学习标签之间的关联性。
实验结果表明,本文方法可以有效地学习标签之间语义关联性,并提升多标签图像分类效果。

提出一种基于知识图谱的通联特征挖掘方法,为电信欺诈案件相关的数据分析及线索挖掘提供技术支持.
基于仿真的通话数据和电信欺诈案件数据,在分布式图数据库中构建知识图谱.
在此基础上使用图遍历及图算法、混合高斯模型,从联系链路、必要人物、核心人物的发现以及社会关系识别这4个维度进行分析挖掘.
在混合高斯模型中,提取9个关键通话特征,从通话模式聚类的角度来识别不同的社会关系.通过实验证明,图遍历及图算法能为电信欺诈人员和团伙的发现提供重要线索.
混合高斯模型识别出了5类社会关系,并且发现涉案人员之间的通话模式具有一定的特殊性,即通话次数多且多发生在凌晨,通话时间较长且保持联系的时间较长.
```

每篇文章的摘要分句，摘要之间间隔一行。


### 2. 选择Pre-train模型

- [ ] BERT
- [x] ALBERT  
- [ ] ELECTRA

基本上取决于有多少算力，如果租得起TPU还是考虑一下这几个模型的large版。由于只有3块V100，所以不考虑base以上的模型。

#### 2.1. 选择ALBERT的原因
[albert_zh](https://github.com/brightmart/albert_zh) 做过大规模中文数据的训练，并且其tiny版本在性能与BERT base接近的情况下，更加轻量级。

#### 2.2. 为什么不使用ELECTRA
我们做科技文献类文本的预训练前期主要用于NER、RE等信息抽取任务，ELECTRA已经过部分研究者测试在该类任务上效果并不好。

### 3. 生成词典

这里参考[turkish-bert](https://github.com/stefan-it/turkish-bert/blob/master/CHEATSHEET.md)进行预训练的过程，使用hugging face提供的 [Tokenizers](https://github.com/huggingface/tokenizers)工具.

[Tokenizers](https://github.com/huggingface/tokenizers)已提供一个针对BERT生成wordpiece词典的[example](https://github.com/huggingface/tokenizers/blob/master/bindings/python/examples/train_bert_wordpiece.py)

使用下述命令进行训练：

```
# install tokenizers
pip install tokenizers
# train wordpiece vocab
python train_bert_wordpiece.py --files file_name --out output_path --name vocab_name
```

这里得到的vocab并没有形如：
```
##一
##二
```
的中文wordpiece，需要手动添加。（至于为什么会有这个，因为albert_zh使用了jieba分词，在mask的时候就有`##一`这样的token）

另外由于科技文献的特殊性，大写、缩写英文术语较多(出现的英文单词大多是这一类)，因此采用的是cased处理，不将其转为lowercase。

**注：** 最终我们还是选择使用[albert_zh](https://github.com/brightmart/albert_zh)提供的vocab，因为其完全覆盖了我们语料中存在的字符，同时因为我们使用其预训练的ckpt作为initial point 继续训练。

### 4. 预训练

#### 4.1. 预训练代码

- [x] TF 1.x version
- [ ] TF 2.x version
- [ ] Pytorch version

#### 4.2. 训练过程
##### 4.2.1. 生成训练数据

```
BERT_BASE_DIR=/home/nlp/data/cs
python3 create_pretraining_data.py --do_whole_word_mask=True --input_file=$BERT_BASE_DIR/cs_raw.txt \
--output_file=$BERT_BASE_DIR/tf_cs_raw.tfrecord --vocab_file=./albert_config/vocab.txt --do_lower_case=False \
--max_seq_length=512 --max_predictions_per_seq=51 --masked_lm_prob=0.10
```
这里跟前面保持一致，不处理英文字母为小写，自己定义`masked_lm_prob`，注意`max_predictions_per_seq = int(max_seq_length * masked_lm_prob)`

##### 4.2.1. 训练模型
写一个shell脚本即可，基本上与albert_zh提供的代码一致。
```
export CUDA_VISIBLE_DEVICES="1,2"
export BERT_BASE_DIR=/home/nlp/data/cs
python3 run_pretraining.py --input_file=$BERT_BASE_DIR/tf*.tfrecord  \
--output_dir=$BERT_BASE_DIR/my_new_model_path --do_train=True --do_eval=True --bert_config_file=$BERT_BASE_DIR/albert_tiny/albert_config_tiny.json \
--train_batch_size=64 --max_seq_length=512 --max_predictions_per_seq=51 \
--num_train_steps=125000 --num_warmup_steps=12500 --learning_rate=0.00176    \
--save_checkpoints_steps=2000  --init_checkpoint=$BERT_BASE_DIR/albert_tiny/albert_model.ckpt
```

这里注意`--max_predictions_per_seq`的值应该和生成训练数据时对应，否则会因为数据不对齐而报错（报错内容是`Invalid argument: Key: masked_lm_positions. Can't parse serialized Example`）。

### 5. 下游任务测试和微调

#### 5.1. 命名实体识别

共有两种方式:

- 直接进行Fine-tuning
- 抽取feature作为word_embeddiing,送入LSTM+CRF

分别进行两种方式的测试,另外加入使用同样语料训练word2vec获得的词向量进行对比.

