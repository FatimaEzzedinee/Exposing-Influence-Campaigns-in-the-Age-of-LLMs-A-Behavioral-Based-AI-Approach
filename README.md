# Exposing Influence Campaigns in the Age of LLMs: A Behavioral-Based AI Approach to Detecting State-Sponsored Trolls

Code for the implementation of the approach presented in "Exposing Influence Campaigns in the Age of LLMs: A Behavioral-Based AI Approach to Detecting State-Sponsored Trolls" by Fatima Ezzeddine, Omran Ayoub, Ihab Sbeity, Ginaluca Nogara, Emilio Ferrara, Silvia Giordano, and Luca Luceri. 


The code is divided in three main scripts, which allow to: 

1. Extract the trajectories of an account: trajectory_main.py

2. Classify an account’s trajectory: RNN-LSTM Classification.ipynb 
          - Trajectory Formation
          - LSTM Model training
          - LSTM Model evaluation
          - Troll Score Computation
          - CDF Plot for the computed scores
          
3. Compute the troll score of an account: Troll Score Classification.ipynb
          - Load the computed scores
          - Compute the threshold that leads to the best AUC, accuracy, precision, recall, f1-score, TNR
          - Display the results


Trolls-related (resp. users-related) tweets are messages where troll (resp. user) accounts have been actively or passively involved.

The actively involved tweets are used to create the ACTIONS within the trajectory and includes:
          - original tweets generated by trolls (resp. users)
          - retweets generated by trolls (resp. users)
          - replies generated by trolls (resp. users)
          - mentions generated by trolls (resp. users)

The passively involved tweets are used to create the STATES within the trajectory and includes:
          - retweets of trolls' (resp. users) generated content
          - replies to trolls' (resp. users) generated content
          - tweets where trolls (resp. users) were mentioned
          
