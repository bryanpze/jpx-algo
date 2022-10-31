# JPX Tokyo Stock Exchange Prediction

## Overview

A bunch of algo trading strategies tested for the JPX Tokyo Stock Exchange Prediction

## Actual Submission

My submission got nullified due to a coding error. After submitting my original submission as a late submission, it received lb score of 0.281, which would mean 11th place out of 1041 teams.

## Original Submission

Based on the paper by Andrew Lo at MIT [Source](http://web.mit.edu/~alo/www/Papers/august07b_2.pdf)
Buy stocks with worst previous one day returns, short the ones with the best previous one day returns. Ignoring transactions costs, the paper showed a Sharpe ratio of 4.47, which was the exact scenario in the competition since there was no transaction costs. Only smallcap stocks are selected due to higher volatility.
