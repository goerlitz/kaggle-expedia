# find intersection of users in training and test data
xzcat train.csv.xz | awk -F, '{print $8}' | sort -n | uniq > train_users
xzcat test.csv.xz | awk -F, '{print $9}' | sort -n | uniq > test_users
join test_users train_users > joined_users

