# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 16:39
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : convert.py

import json

def convert2Dict(obj):
    """
    :param obj:obj is a class
    :return: dict
    """
    dict = {}
    dict.update(obj.__dict__)
    return dict

def convert2Json(obj, filename):
    """
    :param obj: obj is a class
    :return: None
    """
    jsonData = json.dumps(obj)
    with open(filename, 'w') as f:
        json.dump(jsonData, f)

def class2Json(obj, filename):
    """
    :param obj: obj is a class
    :param filename:
    :return:
    """
    dictData = convert2Dict(obj)
    print(dictData)
    convert2Json(dictData, filename)


class mytest(object):

    def __init__(self):
        self.data = 12
        self.name = "asdf"
        self.aa = [[1,3],[2.0,3.0]]

    def append(self,data):
        self.aa.append(data)

a = mytest()
a.append([1,2])
class2Json(a, "data.json")