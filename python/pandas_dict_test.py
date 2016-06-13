import time
#import numpy as np
import pandas as pd
import timeit
#import seaborn as sns

start = time.time()
userMap = pd.read_csv("../data/train_usr-dst-clst-count.csv.gz", index_col = [0,1])
print("done reading {} lines in {} secs.".format(len(userMap.index), time.time() - start))

print("monotonic: {}".format(userMap.index.is_monotonic_increasing))
print("lexsorted: {}".format(userMap.index.is_lexsorted()))

def test():
    userMap.loc[2,8250]

print(userMap.loc[2,8250])
print((2,8250) in userMap.index)
print((2,8250) in userMap.columns)
print(userMap[(2,8250)])

#timeit.timeit('test()', setup="from __main__ import test")

exit(1)

start = time.time()
test = pd.read_csv("../data/test.csv.gz")
print("done reading {} lines in {} secs.".format(len(userMap.index), time.time() - start))

if ((2, 8250) in userMap.index):
    print("found")

start = time.time()
total = 0
found = 0
for tup in test.itertuples():

    if total % 100 == 0:
        print('Processed {} lines...'.format(total))

    if ((tup.user_id, tup.srch_destination_id) in userMap.index):
#        print(userMap.loc[tup.user_id, tup.srch_destination_id])
        found += 1
        print("found in line {}".format(total))


    total += 1

print("done iterating {} lines in {} secs. (found {})".format(total, time.time() - start, found))


#print(userMap.head(20))



#userDict = {r:userMap.ix[r].values for r in userMap.index}
#print(len(userDict))
