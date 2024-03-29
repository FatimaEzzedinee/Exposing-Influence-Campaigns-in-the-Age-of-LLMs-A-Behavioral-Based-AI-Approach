"""
Estimate trolls' (resp. users') rewards in Twitter via the following IRL approaches (implemented by Matthew Alger, 2015):
- Maximum Entropy IRL (Ziebart et al., 2008)
- Deep Maximum Entropy IRL (Wulfmeier et al., 2015)

You can select one of the two approaches by simply commenting/uncommenting line 127/128

This script can be utilized both for trolls and generic users.
For our convenience, we show here only the script that utilize trolls-related tweets to output trolls' estimated rewards.
To adapt it to non-troll accounts (i.e., generic users), you only need to give as input generic users-related tweets.

Trolls-related (resp. users-related) tweets are tweets where troll (resp. users) accounts have been actively or passively involved.

The former class (actively involved) is used to create the ACTIONS of the IRL problem and includes:
- original tweets generated by trolls (resp. users)
- retweets generated by trolls (resp. users)
- replies generated by trolls (resp. users)
- mentions generated by trolls (resp. users)

The latter class (passively involved) is used to create the STATES of the IRL problem and includes:
- retweets of trolls' (resp. users) generated content
- replies to trolls' (resp. users) generated content
- tweets where trolls (resp. users) were mentioned

Finally, the script outputs the estimated rewards in a csv file named "df_results_trolls_IRL.csv". 
You need to change the output file when you run the script for generic users.

Luca Luceri, 2020
luca.luceri@supsi.ch
"""


import pandas as pd
import numpy as np
import math
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from datetime import timedelta
from datetime import datetime 
#import deep_maxent as deep_maxent
#from value_iteration import find_policy
#import maxent as maxent
from utils_trolls import *
from gen_tweet_trajectories_trolls_new import *

#### load data related to trolls (resp. users) 
#### data should be presented in the following way to enable the needed pre-processing

### actively involved tweets
df_RT_a=pd.read_csv("df_RT_a_trolls.csv") # retweets generated by trolls (resp. users)
df_rp_a=pd.read_csv("df_rp_a_trolls.csv") # replies generated by trolls (resp. users)
df_tw_a=pd.read_csv("df_tw_a_trolls.csv") # original tweets generated by trolls (resp. users)
df_m_a=pd.read_csv("df_m_a_trolls.csv") # tweets with mentions generated by trolls (resp. users)

### passively involved tweets
df_RT_m=pd.read_csv("df_RT_m_trolls.csv")  # retweets of trolls' (resp. users) generated content
df_rp_m=pd.read_csv("df_rp_m_trolls.csv") # replies to trolls' (resp. users) generated content
df_m_m=pd.read_csv("df_m_m_trolls.csv") # tweets where trolls (resp. users) were mentioned

### actively involved tweets dataframe
df_author=df_RT_a.append(df_rp_a,ignore_index=True)
df_author=df_author.append(df_tw_a,ignore_index=True)
df_author=df_author.append(df_m_a,ignore_index=True)
df_author.reset_index(inplace = True)
users_subset= pd.unique(df_author.screen_name) 

# IRL parameters
discount = .9
epochs = 1000
learning_rate = 0.01
structure = (3, 3)
l1 = l2 = 0

df_results = pd.DataFrame(columns = ['screen_name','trajectories','state_sequence'])

# threshold parameter
t_a = 5 # threshold to filter out trolls (resp. users) that have not performed at least t_a sharing activities (original tweets +retweets + replies + mentions) 
t_p = 5 # threshold to filter out trolls (resp. users) that have not received at least t_p feedback from other accounts (retweets + replies + mentions) 

count = 0
for user_name in users_subset:
    print(user_name,count)
    
    # creating user-based dataframe
    # actions
    tw_a_u, n_tw_a = create_user_dataframe(df_tw_a,user_name,'screen_name',1,"a") # action: original tweet
    RT_a_u, n_rt_a = create_user_dataframe(df_RT_a,user_name,'screen_name',2,"a") # action: retweet
    rp_a_u, n_rp_a = create_user_dataframe(df_rp_a,user_name,'screen_name',3,"a") # action: reply
    m_a_u, n_m_a = create_user_dataframe(df_m_a,user_name,'screen_name',4,"a") # action: mention
    n_a = n_tw_a+n_rt_a+n_rp_a+n_m_a # number of actions

    # states
    RT_p_u, n_rt_p = create_user_dataframe(df_RT_m,user_name,'user_retweeted',5,"p") # state: got a retweet
    rp_p_u, n_rp_p = create_user_dataframe(df_rp_m,user_name,'in_reply_to_screen_name',6,"p") # state: got a reply
    m_p_u, n_m_p = create_user_dataframe(df_m_m,user_name,'mention',7,"p") # state: got a mention
    n_p = n_rt_p+n_rp_p+n_m_p # number of states
    
    if n_a> t_a and n_p> t_p: # filtering out some users
        
        # creating actions dataframe
        df_active_u = tw_a_u.append(RT_a_u,ignore_index=True)
        df_active_u = df_active_u.append(rp_a_u,ignore_index=True)
        df_active_u = df_active_u.append(m_a_u,ignore_index=True)
        df_active_u = df_active_u.sort_values(by='time') 
        df_active_u.reset_index(inplace = True)
        del df_active_u['index']
        df_active_u = adjust_tweet_df(df_active_u)
        
        # creating states dataframe
        RT_p_u = adjust_retweet_df(RT_p_u)
        rp_p_u = adjust_reply_df(rp_p_u)
        m_p_u = adjust_mention_df(m_p_u)
        df_passive_u = RT_p_u.append(rp_p_u,ignore_index=True)
        df_passive_u = df_passive_u.append(m_p_u,ignore_index=True)
        df_passive_u = df_passive_u.sort_values(by='time') 
        df_passive_u.reset_index(inplace = True)
        del df_passive_u['index']
        
        # create total dataframe
        df_total =merge_df(df_active_u,df_passive_u)

        # IRL
        trajectories, state_sequence,n_states,n_actions,feature_matrix,t_dict,c_dict = tweet_traj_next_reduced(df_total) # compute trajectories and other information
        tp = compute_tp(state_sequence,n_states,n_actions) # compute transition probabilities 
        #r = maxent.irl(feature_matrix, n_actions, discount, tp, trajectories, epochs,learning_rate) # maximum entropy IRL (comment this line if you want to use deep maximum entropy IRL --> line below)
#         r = deep_maxent.irl((feature_matrix.shape[1],) + structure, feature_matrix,n_actions, discount, tp, trajectories, epochs,learning_rate, l1=l1, l2=l2) # deep maximum entropy IRL (comment this line if you want to use maximum entropy IRL --> line above)
        #w = np.linalg.lstsq(feature_matrix,r)[0] # compute weights of each feauture
        
        # save results
        #row = [user_name,r,w]
        row = [user_name, trajectories, state_sequence]
        df_results.loc[count]= row
        count += 1
    else:
        print("user %s has %s actions and %s states" %(user_name,n_a,n_p))

df_results.to_csv("trajectories.csv",index= False) # saverewards in a csv file (NB:change the name of the file for generic users in df_results_users_IRL.csv)





