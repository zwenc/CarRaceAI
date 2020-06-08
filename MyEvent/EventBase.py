# -*- coding: utf-8 -*-
# @Time    : 2020/6/7 17:29
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : EventBase.py

class EventBase(object):

    def __init__(self, sign):
        self.sign = sign

    def setSign(self, sign):
        self.sign = sign