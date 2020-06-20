# -*- coding: utf-8 -*-
# @Time    : 2020/6/20 13:12
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : AIControl.py

import torch
import threading
import time
from car.CarAI import CarAI
from AI.net.net import ActorNetworkUser, ActorNetwork
from AI.config.RLConfig import *

device = torch.device("cpu")

class AIControl(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.actorNetwork = ActorNetwork(STATE_DIM, 100, ACTION_DIM).to(device)
        self.actorNetwork.eval()

        # self.actorNetwork = None
        self.start()

    def run(self):

        if os.path.exists("AI/model/actor_network.pkl"):
            self.actorNetwork.load_state_dict(torch.load("AI/model/actor_network.pkl"))
            print("load actor success!")
        self.actorNetwork.eval()

    def getState(self, carModel):

        return [carModel.carInfo.linearDistance, carModel.carInfo.leftAngleDistance,
                carModel.carInfo.rightAngleDistance,
                carModel.carInfo.leftDistance, carModel.carInfo.rightDistance, carModel.carInfo.speed]

    def step(self, carModel):
        # startTime = time.time()
        state = self.getState(carModel)

        dist = self.actorNetwork(torch.tensor([state], dtype=torch.float).to(device))

        data = dist.sample()
        action = data.clamp(0, 1).cpu().numpy()[0]

        # action = dist.detach().clamp(0, 1).cpu().numpy()[0]

        speed = [action[0], action[1], action[2]]
        Angle = [action[3], action[4], action[5]]

        accItem = [-1, 0, 1]
        accAngle = accItem[Angle.index(max(Angle))]
        accSpeed = accItem[speed.index(max(speed))]

        # print((time.time() - startTime))

        return accSpeed * 0.1, accAngle * 5