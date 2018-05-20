import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import pandas as pd
import os
from os import listdir
from random import randint

class TradingEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.action_space = spaces.Discrete(4)
    
    #consts
    self.stepCost = -0.01
    self.tradeCostPercentage = 0.1
    self.capital = 1000
    self.capitalWin = 10000
    self.capitalLoss = 0
    self.enterUpScoreCol = 'prevBuyDiff'
    self.enterDownScoreCol = 'prevSellDiff'

    self._reset()
	

  def _seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def _step(self, action):
    reward = 0
    ledgerDiff = 0
    finished = False
    balance = (self.balance[self.step-1] if self.step > 0 else self.capital)
    observations = {}

    if action == 0: #enter up
      self.stepEnter = self.step
      self.enterUp = True
      ledgerDiff = (balance*0.1) * -1
      self.stepsSinceLastEnter = 0
    elif action == 1: #enter down
      self.stepEnter = self.step
      self.enterUp = False
      ledgerDiff = (balance*0.1) * -1
      self.stepsSinceLastEnter = 0
    elif action == 2: #hold
      reward += self.stepCost
    elif action ==3: #exit
      total = sum(self.dataRaw.loc[self.stepEnter:self.step, self.enterUpScoreCol if self.enterUp else self.enterDownScoreCol])
      reward += total
      ledgerDiff += total
      self.stepEnter = None

    #output properties for training
    currentBal = balance + ledgerDiff
    self.actions[self.step] = action
    self.rewards[self.step] = reward
    self.balance[self.step] = currentBal
    self.ledger[self.step] = ledgerDiff
    observations = self.data.loc[self.step]
    finished = currentBal <= self.capitalLoss or currentBal >= self.capitalWin
    info = {action: action, reward: reward, balance: currentBal, ledgerDiff: ledgerDiff}
    
    self.step += 1
    return observations, reward, finished, info

  def _reset(self):
    self.data = np.zeros(1)  
    #change each step
    self.step = 0
    self.stepsSinceLastEnter = 0
    self.stepEnter = None
    self.enterUp = False
    self.reward = 0   
    #setup in helper data structs
    self.actions = np.zeros(self.data.shape[0])		
    self.rewards = np.zeros(self.data.shape[0])
    self.balance = np.zeros(self.data.shape[0])
    self.ledger = np.zeros(self.data.shape[0])

  def linear_scale(self, series):
    min_val = series.min()
    max_val = series.max()
    scale = (max_val - min_val) / 2.0
    return series.apply(lambda x:((x - min_val) / scale) - 1.0)

  def setupEnv(dataDir):
    if dataDir != '':
      print('dataDir:' + dataDir)
      self.files = os.listdir(dataDir)
      print(self.files)
      self.currentFile = self.files[randint(0, len(self.files))]
      
      self.dataRaw = pd.read_csv(self.currentFile, header=0, skiprows=1)
      self.data = self._data_setup(self.dataRaw)
	  
      print('Read in: [' + self.currentFile + '] - %s' % (self.data.shape,))
    else:
      self.data = np.zeros(1)   
	
  def _data_setup(self, dataframe):
    output_targets = pd.DataFrame()
    #Hour,Month,buy,buyTotal,sell,sellTotal,spread,prevBuyDiff,prevSellDiff,avgBuy,avgBuyTotal,avgSell,avgSellTotal,avgSpread,ticksPerMinute,avgTicksPerMinute,timeDiff
    output_targets["Hour"] = self.linear_scale(dataframe["Hour"])
    output_targets["Month"] = self.linear_scale(dataframe["Month"])
    output_targets["buyTotal"] = self.linear_scale(dataframe["buyTotal"])
    output_targets["sellTotal"] = self.linear_scale(dataframe["sellTotal"])
    output_targets["spread"] = self.linear_scale(dataframe["spread"])
    output_targets["prevBuyDiff"] = self.linear_scale(dataframe["prevBuyDiff"])
    output_targets["prevSellDiff"] = self.linear_scale(dataframe["prevSellDiff"])
    output_targets["avgBuyTotal"] = self.linear_scale(dataframe["avgBuyTotal"])
    output_targets["avgSellTotal"] = self.linear_scale(dataframe["avgSellTotal"])
    output_targets["avgSpread"] = self.linear_scale(dataframe["avgSpread"])
    output_targets["ticksPerMinute"] = self.linear_scale(dataframe["ticksPerMinute"])
    output_targets["avgTicksPerMinute"] = self.linear_scale(dataframe["avgTicksPerMinute"])
    output_targets["timeDiff"] = self.linear_scale(dataframe["timeDiff"])
    output_targets["points"] = self.linear_scale(dataframe["timeDiff"])

    return output_targets
