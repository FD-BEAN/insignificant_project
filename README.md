# The best is to have three separate type of files for any project:
1. Config file to store the inputs for your function or scripts.
      This is to make it clear to any user of the code what parameters they can adjust
2. Utility file to store reused functions.
      In general, any functionality that you use more than once you should write a function and add to utility file
3. Main file to run the main script for getting final results
4. Optional: Parameters file to store inputs for your scripts.
      This is similar to config, but contains inputs that you may not want other to change


Please use this structure as start point, complete a mini project as required below:
1. Register a chatgpt account and use it when you code
2. Retrieve stock price data from any sources (I have provided data_util to get A shares price)
3. Achieve below:
    * Given any two stock ticker, start, end date, rolling window, and return horizon, gives the correlation and regression statistics of the two stocks
    * Given any one stock ticker, find in the universe the N stocks with highest correlation with that stock, and formulate a weighted basket to hedge the stock
    * Being able to plot the evolution of correlation, regression coefficients
    * Being able to back test the performance of the hedge basket, and consider the stability and rebalance frequency
* 