# -*- coding: utf-8 -*-
# @Time    : 2020/3/5 下午6:37
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : config.py

import time

STATE_DIM = 7
ACTION_DIM = 2
TASK_CONFIG_DIM = 1
EPISODE = 60000
STEP = 10
SAMPLE_NUMS = 32  # 5,10,20
TEST_SAMPLE_NUMS = 5
TASK_CONFIG_LONG = 15
TASK_CONFIG_ENABLE = False
# A3C_MESS_LIST = [500, 500, 500, 500, 500]
A3C_MESS_LIST = [490, 500, 510]
# A3C_MESS_LIST = [ 500]

META_VALUE_NETWORK_LR = 0.00001
TASK_CONFIG_NETWORK_LR = 0.004
ACTOR_NETWORK_LR = 0.00001  # 0.0002

devices = "cuda:0"
TIMESTR = time.strftime("%Y-%m-%dT%H-%M", time.localtime())

# 地址配置
MODELPATH = "AI/out/model/"  # 输出模型地址
PREMODEPATH = "AI/model"     # 预训练模型地址
LOSSSAVEPATH = "./AI/out/rewards"
LOGFILEPATH = "./AI/out/log/"

import os
import sys

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout

        if os.path.exists(LOGFILEPATH) is not True:
            os.makedirs(LOGFILEPATH)

        self.filename = LOGFILEPATH + TIMESTR + "-" + filename
        self.log = open(self.filename, "wt")
        self.log.truncate()
        self.log.close()

    def write(self, message):
        self.terminal.write(message)
        with open(self.filename, "a") as f:
            f.write(message)

    def flush(self):
        pass


path = os.path.abspath(os.path.dirname(__file__))
type = sys.getfilesystemencoding()
sys.stdout = Logger('out.txt')
