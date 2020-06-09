# -*- coding: utf-8 -*-
# @Time    : 2020/6/9 18:10
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : RacingTrack.py

import os
from tools.convert import *
import random

class RacingTrack(object):

    def __init__(self, MapFileName):
        self.MapFileName = MapFileName
        self.hasRecord = False
        self.race = []
        self.read()

    def clear(self):
        self.race = []

    def append(self, pos, angle, speed):
        self.race.append([pos[0], pos[1], angle, speed])

    def write(self):
        filename, ext = self.MapFileName.split(".")
        filePath = "config/mapJson/" + filename + ".json"
        class2Json(self, filePath)

    def read(self):
        filename, ext = self.MapFileName.split(".")
        filePath = "config/mapJson/" + filename + ".json"

        if os.path.exists(filePath) is False:
            self.hasRecord = False
            return

        self.hasRecord = True
        data = eval(readJson(filePath), {'true': 0, 'false': 1})

        self.race = data["race"]

    def __getitem__(self, item):

        if item < len(self.race):
            return self.race[item]

    def randomGetItem(self):
        return random.sample(self.race, 1)


if __name__ == "__main__":
    temp = RacingTrack("aaa.png")
    temp.append([1, 2], 1, 1)
    temp.write()

    xxx = RacingTrack("aaa.png")
    xxx.read()
    print(xxx.race)
