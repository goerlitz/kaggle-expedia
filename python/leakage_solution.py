import sys
import gzip
import datetime
from heapq import nlargest
from operator import itemgetter
from collections import defaultdict

trainfile = "../data/train.csv.gz"
testfile  = "../data/test.csv.gz"

ulc_odd_map = defaultdict(lambda: defaultdict(int))
sdi_odd_map = defaultdict(lambda: defaultdict(int))
uid_sdi_map = defaultdict(lambda: defaultdict(int))
best_hotels_search_dest = defaultdict(lambda: defaultdict(int))
best_hotels_search_dest1 = defaultdict(lambda: defaultdict(int))
best_hotel_country = defaultdict(lambda: defaultdict(int))
popular_hotel_cluster = defaultdict(int)

# argument parsing
if len(sys.argv) > 2:
    trainfile = sys.argv[1]
    testfile = sys.argv[2]
else:
    print("using defaul train and test files.")

print("reading train '{}' and test '{}'.".format(trainfile, testfile))


def key_ratio(map):
    """
    Determine the ratio of major keys to minor keys.
    A ration of 1 means that each major key has only one minor key.
    """
    map_keys = [len(map[key].keys()) for key in map.keys()]
    if len(map_keys) == 0:
        return 0
    return sum(map_keys) / float(len(map_keys))


def explore():
    """
    exploration of training data.
    """

    total = 0

    print('Reading training data...')
    with gzip.open(trainfile, "r") as f:

        # ignore header
        f.readline()

        while 1:
            line = f.readline().strip()

            if line == '':
                break

            total += 1

            if total % 10000000 == 0:
                print('Read {} lines...'.format(total))


            arr = line.split(",")

            # feature assignment
            book_year = int(arr[0][:4])
            user_location_city = arr[5]
            orig_destination_distance = arr[6]
            user_id = arr[7]
            srch_destination_id = arr[16]
            is_booking = int(arr[18])
            hotel_country = arr[21]
            hotel_market = arr[22]
            hotel_cluster = arr[23]

            append_1 = 3 + 17*is_booking
            append_2 = 1 + 5*is_booking

            # user city + distance is almost unique for hotel_cluster
            if user_location_city != '' and orig_destination_distance != '':
                ulc_odd_map[(user_location_city, orig_destination_distance)][hotel_cluster] += 1

            # search destination + distance is almost unique for hotel_cluster
#            if srch_destination_id != '' and orig_destination_distance != '':
#                sdi_odd_map[(srch_destination_id, orig_destination_distance)][hotel_cluster] += 1

            uid_sdi_map[(user_id, srch_destination_id, book_year)][hotel_cluster] += 1

            if srch_destination_id != '' and hotel_country != '' and hotel_market != '' and book_year == 2014:
                best_hotels_search_dest[(srch_destination_id, hotel_country, hotel_market)][hotel_cluster] += append_1

            if srch_destination_id != '':
                best_hotels_search_dest1[srch_destination_id][hotel_cluster] += append_1

            if hotel_country != '':
                best_hotel_country[hotel_country][hotel_cluster] += append_2

            popular_hotel_cluster[hotel_cluster] += 1

    print("read {} lines from train.".format(total))

    print("usr_loc_cty/dist map has ratio {}.".format(key_ratio(ulc_odd_map)))
    print("srch_dst_id/dist map has ratio {}.".format(key_ratio(sdi_odd_map)))
    print("user_id/srch_dst map has ratio {}.".format(key_ratio(uid_sdi_map)))

    #ulc: 9563696 keys, sum: 10105718, ratio: 1.05667495077
    #sdi: 11456801 keys, sum: 11929413, ratio: 1.0412516548

    match_ulc = 0
    match_sdi = 0
    match_all = 0
    match_uid = 0

    print('Prepage submission...')
    now = datetime.datetime.now()
    path = 'submission_' + str(now.strftime("%Y-%m-%d-%H-%M")) + '.csv.gz'

    print('Reading test data...')
    with gzip.open(testfile, "r") as f, gzip.open(path, "w") as out:

        # ignore header
        head = f.readline()
        out.write("id,hotel_cluster\n")
        total = 0

        topclasters = nlargest(5, sorted(popular_hotel_cluster.items()), key=itemgetter(1))

        while 1:
            line = f.readline().strip()

            if line == '':
                break

            total += 1

            if total % 1000000 == 0:
                print('Read {} lines...'.format(total))


            arr = line.split(",")

            id = arr[0]
            user_location_city = arr[6]
            user_id = arr[8]
            orig_destination_distance = arr[7]
            srch_destination_id = arr[17]

            out.write(str(id) + ',')

            # num matches user_loc + dist
#            if user_location_city != '' and orig_destination_distance != '' and (user_location_city, orig_destination_distance) in ulc_odd_map: match_ulc += 1

            # num matches srch_dest + dist
#            if srch_destination_id != '' and orig_destination_distance != '' and (srch_destination_id, orig_destination_distance) in sdi_odd_map: match_sdi += 1

            # num matches user_loc + dist && srch_des + dist
#            if (user_location_city != '' and orig_destination_distance != '' and (user_location_city, orig_destination_distance) in ulc_odd_map) or \
#                    (srch_destination_id != '' and orig_destination_distance != '' and (srch_destination_id, orig_destination_distance) in sdi_odd_map) :
#                match_all += 1

#            if (user_id, srch_destination_id) in uid_sdi_map: match_uid += 1

#            if (user_location_city != '' and orig_destination_distance != '' and (user_location_city, orig_destination_distance) in ulc_odd_map) or \
#                (user_id, srch_destination_id) in uid_sdi_map: match_all += 1

            top5 = []

            key = (user_location_city, orig_destination_distance)
            if key in ulc_odd_map:
                clusters = ulc_odd_map[key]
                top_clst = nlargest(5, sorted(clusters.items()), key=itemgetter(1))
                # intersection of filled
                for i in range(len(top_clst)):
                    if top_clst[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + top_clst[i][0])
                    top5.append(top_clst[i][0])

            # key = (srch_destination_id, orig_destination_distance)
            # if key in sdi_odd_map:
            #     clusters = sdi_odd_map[key]
            #     top_clst = nlargest(5, sorted(clusters.items()), key=itemgetter(1))
            #     # intersection of filled
            #     for i in range(len(top_clst)):
            #         if top_clst[i][0] in top5:
            #             continue
            #         if len(top5) == 5:
            #             break
            #         out.write(' ' + top_clst[i][0])
            #         top5.append(top_clst[i][0])

            key = (user_id, srch_destination_id, 2014)
            if key in uid_sdi_map:
                clusters = uid_sdi_map[key]
                top_clst = nlargest(5, sorted(clusters.items()), key=itemgetter(1))
                # intersection of filled
                for i in range(len(top_clst)):
                    if top_clst[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + top_clst[i][0])
                    top5.append(top_clst[i][0])

            key = (user_id, srch_destination_id, 2013)
            if key in uid_sdi_map:
                clusters = uid_sdi_map[key]
                top_clst = nlargest(5, sorted(clusters.items()), key=itemgetter(1))
                # intersection of filled
                for i in range(len(top_clst)):
                    if top_clst[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + top_clst[i][0])
                    top5.append(top_clst[i][0])

            s2 = (srch_destination_id, hotel_country, hotel_market)
            if s2 in best_hotels_search_dest:
                d = best_hotels_search_dest[s2]
                topitems = nlargest(5, d.items(), key=itemgetter(1))
                for i in range(len(topitems)):
                    if topitems[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + topitems[i][0])
                    top5.append(topitems[i][0])
            elif srch_destination_id in best_hotels_search_dest1:
                d = best_hotels_search_dest1[srch_destination_id]
                topitems = nlargest(5, d.items(), key=itemgetter(1))
                for i in range(len(topitems)):
                    if topitems[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + topitems[i][0])
                    top5.append(topitems[i][0])

            if hotel_country in best_hotel_country:
                d = best_hotel_country[hotel_country]
                topitems = nlargest(5, d.items(), key=itemgetter(1))
                for i in range(len(topitems)):
                    if topitems[i][0] in top5:
                        continue
                    if len(top5) == 5:
                        break
                    out.write(' ' + topitems[i][0])
                    top5.append(topitems[i][0])

            for i in range(len(topclasters)):
                if topclasters[i][0] in top5:
                    continue
                if len(top5) == 5:
                    break
                out.write(' ' + topclasters[i][0])
                top5.append(topclasters[i][0])


            out.write("\n")

    print("read {} lines from test.".format(total))
    print("found {} ulc matches.".format(match_ulc))
    print("found {} sdi matches.".format(match_sdi))
    print("found {} total matches.".format(match_all))
    print("found {} uid_srch matches.".format(match_uid))

    #2528244 lines from test.
    #found 852711 ulc matches.
    #found 681912 sdi matches.
    #found 853771 total matches.

explore()
