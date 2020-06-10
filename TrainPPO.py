# -*- coding: utf-8 -*-
# @Time    : 2020/6/10 18:47
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : TrainPPO.py

from AI.Model import *

if __name__ == "__main__":

    aaa = Mymodel()

    for i in range(EPISODE):
        aaa.run()