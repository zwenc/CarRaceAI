# -*- coding: utf-8 -*-
# @Time    : 2020/3/5 下午6:35
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : net.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.distributions import Normal

class ActorNetwork(nn.Module):

    def __init__(self, input_size, hidden_size=50, action_size=1):
        super(ActorNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.activate1 = torch.nn.LeakyReLU(0.01)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.activate2 = torch.nn.LeakyReLU(0.01)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.activate3 = torch.nn.LeakyReLU(0.01)

        self.mu = nn.Linear(hidden_size, action_size)
        self.sigma = nn.Linear(hidden_size, action_size)

        # for m in self.children():
        #     if isinstance(m, (nn.Linear)):
        #         m.weight.data.normal_(0, 0.02)
        #         m.bias.data.zero_()

    def forward(self, x):
        x = self.activate1(self.fc1(x))
        x = self.activate2(self.fc2(x))
        x = self.activate3(self.fc3(x))

        mu = torch.tanh(self.mu(x)) * 0.5    # 均值
        sigma = F.softplus(self.sigma(x))    # 标准差

        out = Normal(loc=mu, scale=sigma)    # 正太分布，（输出是很多值，需要使用sample对其进行采样）

        return out


class MetaValueNetwork(nn.Module):

    def __init__(self, input_size, hidden_size, output_size):
        super(MetaValueNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.activate1 = torch.nn.LeakyReLU(0.001)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.activate2 = torch.nn.LeakyReLU(0.001)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.activate3 = torch.nn.LeakyReLU(0.001)
        self.fc4 = nn.Linear(hidden_size, output_size)

        # for m in self.children():
        #     if isinstance(m,(nn.Linear)):
        #         m.weight.data.normal_(0, 0.5)
        #         m.bias.data.zero_()

    def forward(self, x):
        out = self.activate1(self.fc1(x))
        out = self.activate2(self.fc2(out))
        out = self.activate3(self.fc3(out))
        out = self.fc4(out)
        return out


class TaskConfigNetwork(nn.Module):

    def __init__(self, input_size, hidden_size, num_layers, output_size, device=torch.device('cpu')):
        super(TaskConfigNetwork, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.device = device
        self.h0 = None
        self.c0 = None

    def forward(self, x, initEnable = True):
        # Set initial states
        if initEnable or self.h0 is None or self.c0 is None:
            self.h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device)
            self.c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device)

        # Forward propagate RNN
        out, (self.h0, self.c0) = self.lstm(x, (self.h0, self.c0))
        # Decode hidden state of last time step
        out = self.fc(out[:, -1, :])

        self.h0 = self.h0.clone().detach()
        self.c0 = self.c0.clone().detach()
        return out