# -*- coding: utf-8 -*-
# @Time    : 2020/3/5 下午6:38
# @Author  : zwenc
# @Email   : zwence@163.com
# @File    : myModel.py

import numpy as np
import tensorboardX

# from Path_S import Path as env
# from actions import draw
from CarGameAI import CarGameAI as env
from AI.config.RLConfig import *
from AI.net.net import *
from config.MapConfig import *

device = torch.device(devices)
tensorVis = tensorboardX.SummaryWriter("AI/out/runs/{}".format(time.strftime("%Y-%m-%dT%H-%M", time.localtime())))


def roll_out(actor_network, task, sample_nums):
    states = []
    actions = []
    rewards = []
    score = []
    is_done = False
    state = task.mstate
    for j in range(sample_nums):
        states.append(state)
        dist = actor_network(torch.tensor([state], dtype=torch.float).to(device))

        data = dist.sample()
        action = data.clamp(0, 1).cpu().numpy()[0]
        # accSpeed = data[0, 0]
        # accSpeed = accSpeed.clamp(-MAXSPEEDACC, MAXSPEEDACC).cpu().numpy()
        #
        # accAngle = data[0, 1]
        # accAngle = accAngle.clamp(-MAXANGLESPEED, MAXANGLESPEED).cpu().numpy()

        next_state, reward, done = task.step(action)

        actions.append(data.cpu().numpy()[0])
        rewards.append([(reward + 8) / 8])
        final_state = next_state
        state = next_state
        score.append(reward)

        if done:
            is_done = True
            break

    return np.array(states), np.array(actions), rewards, is_done, np.array(final_state), score


def discount_reward(r, gamma, final_r):
    discounted_r = np.zeros_like(r)
    running_add = final_r
    for t in reversed(range(0, len(r))):
        running_add = running_add * gamma + r[t][0]
        discounted_r[t] = running_add
    return discounted_r


class Mymodel(object):
    # META_VALUE_INPUT_DIM = STATE_DIM
    META_VALUE_INPUT_DIM = STATE_DIM + TASK_CONFIG_DIM if TASK_CONFIG_ENABLE else STATE_DIM
    TASK_CONFIG_INPUT_DIM = STATE_DIM + ACTION_DIM + 1  # 14
    CONTAINER_MAX_LEN = 1

    def __init__(self, name="1", LoadDict=False, A3C=False,
                 PubilcModel=None, LrNum=1):

        self.pubilcModel = PubilcModel
        self.loadDicts = LoadDict
        self.A3C = A3C
        self.name = name
        self.episode = 0

        # create meta, tastConfig and actor network
        self.metaValueNetwork = MetaValueNetwork(input_size=self.META_VALUE_INPUT_DIM,
                                                 hidden_size=50, output_size=1).to(device)
        self.taskConfigNetwork = TaskConfigNetwork(input_size=self.TASK_CONFIG_INPUT_DIM,
                                                   hidden_size=50, num_layers=1,
                                                   output_size=TASK_CONFIG_DIM, device=device).to(device)

        # in ppo method, need to create two actor
        self.actorNetwork = ActorNetwork(STATE_DIM, 100, ACTION_DIM).to(device)
        self.actorNetworkOld = ActorNetwork(STATE_DIM, 100, ACTION_DIM).to(device)

        # use Adam to create the optim
        self.metaValueNetworkOptim = torch.optim.Adam(self.metaValueNetwork.parameters(),
                                                      lr=META_VALUE_NETWORK_LR / LrNum)
        self.taskConfigNetworkOptim = torch.optim.Adam(self.taskConfigNetwork.parameters(),
                                                       lr=TASK_CONFIG_NETWORK_LR / LrNum)
        self.actorNetworkOptim = torch.optim.Adam(self.actorNetwork.parameters(),
                                                  lr=ACTOR_NETWORK_LR)

        # init the environment
        self.taskEnv = env(mapIndex=1, initPosIndex=0)
        self.taskEnv.reset()

        # init the test environment
        self.testEnv = env(mapIndex=1, initPosIndex=0)
        self.testEnv.reset()

        # init the data container
        self.container = []
        self.containerLen = 0

        # init some flag
        self.miniDistance = 10  # record the mini distance
        self.currentDistance = 10
        self.rewardsContainer = []  # record rewards
        self.steps = 0
        self.maxSteps = 0

        # init runningReward and relative info
        self.runningReward = 0
        self.roundSteps = 0  # record steps, update the runningReward every 600 steps
        self.score = 0  # recode score
        self.roundindex = 0

        self.LstmSteps = 0
        self.LstmdataRecord = 0
        self.LstmIndex = 0

        # load dict
        if self.loadDicts:
            self.loadDict()

    # add data to container
    def dataAppend(self, data):
        if len(self.container) < self.CONTAINER_MAX_LEN:
            self.containerLen = self.CONTAINER_MAX_LEN + 1
            self.container.append(data)
            return

        if self.containerLen >= self.CONTAINER_MAX_LEN - 1:
            self.containerLen = 0

        self.container[self.containerLen] = data
        self.containerLen = self.containerLen + 1

    def saveLstmScore(self, LstmScore):
        LstmScore = LstmScore.data.numpy()
        LstmScore = LstmScore.reshape(LstmScore.shape[0])

        if (self.LstmSteps + len(LstmScore.tolist())) > 600:
            temp = LstmScore[:(600 - self.LstmSteps)]
            self.LstmdataRecord = self.LstmdataRecord + np.sum(temp)
            self.LstmdataRecord = self.LstmdataRecord / 600

            tensorVis.add_scalar("LstmdataRecord/" + self.name, self.LstmdataRecord, self.LstmIndex)

            with open(LOSSSAVEPATH + '/LstmDataRecord_' +
                      '{}_'.format(TIMESTR) + self.name + '.csv', 'a+') \
                    as fp:
                fp.write(str(self.LstmdataRecord) + "\n")
                fp.close()

            self.LstmIndex = self.LstmIndex + 1
            self.LstmSteps = 0
            self.LstmdataRecord = 0

        else:
            self.LstmdataRecord = self.LstmdataRecord + np.sum(LstmScore)
            self.LstmSteps = self.LstmSteps + len(LstmScore.tolist())

    def saveReward(self, reward):
        if (self.roundSteps + len(reward)) >= 600:
            for index in range(600 - self.roundSteps):
                self.score = self.score + reward[index]

            if self.runningReward == 0:
                self.runningReward = self.score
            else:
                self.runningReward = self.score * 0.1 + self.runningReward * 0.9

            # tensorVis.add_scalar("reward/" + self.name, self.runningReward, self.roundindex)

            with open(LOSSSAVEPATH + '/rewards_origin_' +
                      '{}_'.format(TIMESTR) + self.name + '.csv', 'a+') \
                    as fp:
                fp.write(str(self.score) + "\n")
                fp.close()

            self.roundindex = self.roundindex + 1
            self.score = 0
            self.roundSteps = 0
            self.taskEnv.reset()
        else:
            for x in reward:
                self.score = self.score + x

            self.roundSteps = self.roundSteps + len(reward)

    # data collect
    def sampleData(self):
        states, actions, rewards, isDone, finalState, score = roll_out(self.actorNetwork,
                                                                       self.taskEnv,
                                                                       SAMPLE_NUMS)

        self.dataAppend([states, actions, rewards, finalState, isDone])
        self.saveReward(score)

        if isDone:
            self.taskEnv.reset()

        return len(actions)

    def train(self):
        self.actorNetwork.train()

        self.actorNetworkOld.load_state_dict(self.actorNetwork.state_dict())

        for states, actions, rewards, finalState, isDone in self.container:

            a = torch.tensor(np.vstack(actions), dtype=torch.float, requires_grad=True).to(
                device)  # get actor with grad
            s = torch.tensor(np.vstack(states), dtype=torch.float, requires_grad=True).to(
                device)  # get state with grad

            s_ = torch.tensor(finalState, dtype=torch.float).to(device)

            final_r = self.metaValueNetwork(s_)

            discount_r = discount_reward(rewards, DELAYGAMMA, final_r.cpu().item())
            discount_r = torch.tensor(discount_r, dtype=torch.float, requires_grad=False).view(-1, 1).to(device)

            with torch.no_grad():
                A_v = discount_r - self.metaValueNetwork(s.detach())

                dist_old = self.actorNetworkOld(s.detach())
                action_log_probs_old = dist_old.log_prob(a.detach())

            LossCount = torch.tensor([0, 0], dtype=torch.float)
            for step in range(STEP):

                dist = self.actorNetwork(s)
                action_log_probs = dist.log_prob(a)
                ratio = torch.exp(action_log_probs - action_log_probs_old.detach())

                surr1 = ratio * A_v
                surr2 = torch.clamp(ratio, 1.0 - 0.2,
                                    1.0 + 0.2) * A_v

                action_loss = -torch.min(surr1, surr2).mean()
                self.actorNetworkOptim.zero_grad()

                if torch.isnan(action_loss):
                    print("Nane")

                action_loss.backward()

                if torch.isnan(self.actorNetwork.fc1.weight.grad[0, 0]):
                    print("ad")

                self.actorNetworkOptim.step()

                value_loss = F.mse_loss(discount_r, self.metaValueNetwork(s))
                self.metaValueNetworkOptim.zero_grad()
                value_loss.backward()
                self.metaValueNetworkOptim.step()

                LossCount[0] = LossCount[0] + action_loss.cpu().item()
                LossCount[1] = LossCount[1] + value_loss.cpu().item()
            LossCount[0] = LossCount[0] / STEP
            LossCount[1] = LossCount[1] / STEP
            tensorVis.add_scalar("actor/actorLoss" + self.name, LossCount[0], self.episode)
            tensorVis.add_scalar("value/valueLoss" + self.name, LossCount[1], self.episode)

            self.saveLoss(LossCount[0], LossCount[1])

    def saveLoss(self, actorLoss, valueLoss):
        with open(LOSSSAVEPATH + '/rewards_origin_' +
                  '{}_actorLoss_'.format(TIMESTR) + self.name + '.csv', 'a+') \
                as fp:
            fp.write(str(actorLoss) + "\n")
            fp.close()
        with open(LOSSSAVEPATH + '/rewards_origin_' +
                  '{}_valueLoss_'.format(TIMESTR) + self.name + '.csv', 'a+') \
                as fp:
            fp.write(str(valueLoss) + "\n")
            fp.close()

    def shareGrads(self, model, shareModel):

        for param, shareParam in zip(model.parameters(), shareModel.parameters()):
            # if shareParam.grad is None:
            shareParam.grad = param.grad.data.clone()

    def modelTest(self, trainSteps):
        self.actorNetwork.eval()
        state = self.testEnv.reset()
        # result = 0
        # test_task = env(distance_error_max=0.5, uk=self.uk, mess=self.mess)
        # # reward path infos
        # B_distance_error, Q_distance_error = [], []
        # angle_error = []
        # betas = []
        # B_x = []
        # B_y = []
        # Q_x = []
        # Q_y = []
        #
        # state = test_task.reset()
        temp = []
        for test_step in range(2000):
            dist = self.actorNetwork(Variable(torch.Tensor([state])).to(device))

            data = dist.sample()
            action = data.clamp(0, 1).cpu().numpy()[0]
            # accSpeed = data[0, 0]
            # accSpeed = accSpeed.clamp(-MAXSPEEDACC, MAXSPEEDACC).cpu().numpy()
            #
            # accAngle = data[0, 1]
            # accAngle = accAngle.clamp(-MAXANGLESPEED, MAXANGLESPEED).cpu().numpy()

            next_state, reward, done = self.testEnv.step(action)
            state = next_state
            temp.append(action)

        #     B_distance_error.append(infos['B_distance_error'])
        #     Q_distance_error.append(infos['Q_distance_error'])
        #     angle_error.append(infos['angle_error'])
        #     betas.append(infos['beta'] * 180 / np.pi)
        #     B_x.append(infos['B'][0])
        #     B_y.append(infos['B'][1])
        #     Q_x.append(infos['Q'][0])
        #     Q_y.append(infos['Q'][1])
        #
            if done or test_step == 1999:
                print("episode:", self.episode, "task:", self.name, "test result:", test_step)
                # print(temp)
                break
        #
        # # if test_step > 100:
        # #     draw(B_x, B_y, Q_x, Q_y, B_distance_error, angle_error, betas, best=True, name=self.name)
        #
        # print("episode:", self.episode, "task:", self.name, "test result:", result / 10.0, "test_step:",
        #       test_step, "train_step:", trainSteps, "max steps:", self.maxSteps)

        # self.rewardsContainer.append(result)
        # self.currentDistance = np.mean([abs(v) for v in B_distance_error])
        # if self.miniDistance > self.currentDistance:
        #     self.miniDistance = self.currentDistance
        #     self.saveDict(name="best")  # save dict, called best
        self.testEnv.saveImage()


    def loadDict(self):
        exterLstm = "LSTM" if TASK_CONFIG_ENABLE else ""
        if os.path.exists("model/meta_value_network_cartpole" + exterLstm + "best" + self.name + ".pkl"):
            self.metaValueNetwork.load_state_dict(torch.load("model/meta_value_network_cartpole"
                                                             + exterLstm + "best" + self.name + ".pkl"))
        if os.path.exists("model/meta_value_network_cartpole" + exterLstm + "best" + self.name + ".pkl"):
            self.taskConfigNetwork.load_state_dict(torch.load("model/task_config_network_cartpole"
                                                              + exterLstm + "best" + self.name + ".pkl"))
        # if os.path.exists("model/actor_network_cartpole" +exterLstm+ self.name + ".pkl"):
        #     self.actorNetwork.load_state_dict(torch.load("model/actor_network_cartpole" + self.name + ".pkl"))

        print("load dict success !")

    def saveDict(self, name=""):
        exterLstm = "LSTM" if TASK_CONFIG_ENABLE else ""

        if os.path.exists(MODELPATH + TIMESTR) is not True:
            os.makedirs(MODELPATH + TIMESTR)

        torch.save(self.metaValueNetwork.state_dict(),
                   MODELPATH + TIMESTR + "/meta_value_network_cartpole" + exterLstm + name + self.name + ".pkl")

        torch.save(self.taskConfigNetwork.state_dict(),
                   MODELPATH + TIMESTR + "/task_config_network_cartpole" + exterLstm + name + self.name + ".pkl")

        torch.save(self.actorNetwork.state_dict(),
                   MODELPATH + TIMESTR + "/actor_network_cartpole" + exterLstm + name + self.name + ".pkl")

    def loadPublicDict(self):
        if self.A3C:
            if self.pubilcModel is not None:
                self.metaValueNetwork.load_state_dict(self.pubilcModel.metaValueNetwork.state_dict())
                # self.actorNetwork.load_state_dict(self.pubilcModel.actorNetwork.state_dict())
                if TASK_CONFIG_ENABLE:
                    self.taskConfigNetwork.load_state_dict(self.pubilcModel.taskConfigNetwork.state_dict())

    def run(self, enable=True):
        if enable == False:
            self.episode = self.episode + 1
            return

        if self.episode % 10 == 0:
            self.modelTest(self.steps)
            self.maxSteps = 0

        # if self.episode % 1 == 0:
        #     self.loadPublicDict()

        self.episode = self.episode + 1
        self.steps = self.sampleData()  # data collect

        if self.maxSteps < self.steps:
            self.maxSteps = self.steps

        self.train()

        # self.saveDict()

if __name__ == "__main__":

    aaa = Mymodel()

    for i in range(EPISODE):
        aaa.run()
