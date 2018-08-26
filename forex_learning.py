
#! pip3 install --upgrade tensorflow
#! pip3 install gym
#! pip3 install numpy
#! pip3 install matplotlib



import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import gym
import matplotlib.pyplot as plt

try:
    xrange = xrange
except:
    xrange = range
	
env = gym.make('TradingEnv-v0')

#path = 'D:\Data\Agent-127.0.0.1-3000\MQL5\Files'
path = r'C:\Users\klilley\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\\'
print(path)
env.setupEnv(path)
gamma = 0.99

""" take 1D float array of rewards and compute discounted reward """
def discount_rewards(rewards):
    #setup empty array of the same size as rewards with zeros
    discounted_rewards = np.zeros_like(rewards)
    #init the running total
    running_add = 0
    for t in reversed(xrange(0, rewards.size)):
        #discount the running reward by 1% and add it to current
        running_add = running_add * gamma + r[t]
        
        discounted_rewards[t] = running_add
    return discounted_rewards
	
	
class agent():
    def __init__(self, learnRate, state_size, action_size, hidden_size):
        #set the state on the agent it will be fed in a feed Dictionary
        self.state_in= tf.placeholder(shape=[None,state_size],dtype=tf.float32)
        
        #the hidden NN that takes in the state, has hidden_size nodes in NN with the relu activation function
        hidden = slim.fully_connected(self.state_in, hidden_size, biases_initializer=None, activation_fn=tf.nn.relu)
        
        #takes in the hidden layer and outputs 2 actions 
        self.output = slim.fully_connected(hidden,action_size,activation_fn=tf.nn.softmax,biases_initializer=None)
        
        #chooses the action that has the highest certaintiy
        self.chosen_action = tf.argmax(self.output,1)

        #The next six lines establish the training proceedure. We feed the reward and chosen action into the network to compute the loss, and use it to update the network.
        
        
        self.reward_holder = tf.placeholder(shape=[None],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[None],dtype=tf.int32)
        
        self.indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
        self.responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), self.indexes)

        self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs)*self.reward_holder)
        
        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for idx,var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32,name=str(idx)+'_holder')
            self.gradient_holders.append(placeholder)
        
        self.gradients = tf.gradients(self.loss,tvars)
        
        optimizer = tf.train.AdamOptimizer(learning_rate=learnRate)
        self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))
		
		
tf.reset_default_graph() #Clear the Tensorflow graph
myAgent = agent(learnRate=0.01, state_size=4, action_size=2, hidden_size=8) #Load the agent.

total_episodes = 5000 #Set total number of episodes to train agent on.
max_ep = 999
update_frequency = 5

init = tf.global_variables_initializer()

# Launch the tensorflow graph
with tf.Session() as sess:
    sess.run(init)
    i = 0
    total_reward = []
    total_lenght = []
        
    gradBuffer = sess.run(tf.trainable_variables())
    for ix,grad in enumerate(gradBuffer):
        gradBuffer[ix] = grad * 0
        
    while i < total_episodes:
        s = env.reset()
        env.setupEnv(path) #'D:\Data\Agent-127.0.0.1-3000\MQL5\Files')
        running_reward = 0
        ep_history = []
        for j in range(max_ep):
            #Probabilistically pick an action given our network outputs.
            a_dist = sess.run(myAgent.output,feed_dict={myAgent.state_in:[s]})
            a = np.random.choice(a_dist[0],p=a_dist[0])
            a = np.argmax(a_dist == a)

            s1,r,d,_ = env.step(a) #Get our reward for taking an action given a bandit.
            ep_history.append([s,a,r,s1])
            s = s1
            running_reward += r
            if d == True:
                #Update the network.
                ep_history = np.array(ep_history)
                ep_history[:,2] = discount_rewards(ep_history[:,2])
                feed_dict={myAgent.reward_holder:ep_history[:,2], myAgent.action_holder:ep_history[:,1],myAgent.state_in:np.vstack(ep_history[:,0])}
                grads = sess.run(myAgent.gradients, feed_dict=feed_dict)
                for idx,grad in enumerate(grads):
                    gradBuffer[idx] += grad

                if i % update_frequency == 0 and i != 0:
                    feed_dict= dictionary = dict(zip(myAgent.gradient_holders, gradBuffer))
                    _ = sess.run(myAgent.update_batch, feed_dict=feed_dict)
                    for ix,grad in enumerate(gradBuffer):
                        gradBuffer[ix] = grad * 0
						
                total_reward.append(running_reward)
                total_lenght.append(j)
                break
				
				
            #Update our running tally of scores.
        if i % 100 == 0:
            print(np.mean(total_reward[-100:]))
        i += 1