Some content from

https://towardsdatascience.com/how-to-make-your-pandas-operation-100x-faster-81ebcd09265c

Main Idea: Shows numpy vectorized procedure 1000x faster than iterrows(never use) itertuples or somewhat
 faster than apply. 

https://gist.github.com/yifeihuang/69dfd7fa0c6effbf46dffc2af853067e#file-parallel_apply-ipynb

https://gist.github.com/yifeihuang

### High Performance Python Notes:

timit module is only good to runa seprate function

other options:
- using /usr/bin/time os command to run whole module
- using cProfile module (about 50% overhead)
