from GPano import *
import GPano
import csv,itertools
import pandas as pd
import multiprocessing as mp
import database_ops as db_ops


def downloadImg(lon,lat,saved_path):
    gpano = GPano.GPano()
    degrees = [90,270]
    # saved_path = "J:\Research\Trees\west_trees"
    data = gpano.getPanoJsonfrmLonat(lon, lat)
    # print(data)
    car_pano = data.get("Location")
    car_lat = car_pano.get("lat")
    car_lon = car_pano.get("lng")
    # print(car_lon)
    # angle = gpano.getDegreeOfTwoLonlat(lat,lon,float(car_lat),float(car_lon))
    angle = gpano.getDegreeOfTwoLonlat(float(car_lat), float(car_lon), lat, lon)  #  see from float(car_lat), float(car_lon) to lon/lat

    panoId = data["Location"]["panoId"]
    # ---------------------------------------------------------------------------
    projection = data.get("Projection")
    pano_yaw_deg = float(projection.get("pano_yaw_deg"))
    print('angle, pano_yaw_deg: ', angle, pano_yaw_deg)
    # degrees.append(angle)

    find_min = [abs(pano_yaw_deg + deg - angle) % 360 for deg in degrees ]
    find_min2 = []
    for f in find_min:
        if f > 180:
            find_min2.append(abs(f-360))
        else:
            find_min2.append(f)

    index = find_min2.index(min(find_min2))
    # print(data)
    yaw = degrees[index]+pano_yaw_deg
    yaw = yaw % 360
    # if yaw > 360:
    #     yaw = yaw - 360
    # if yaw < 0:
    #     yaw = yaw + 360
    # print(yaw)
    # getDegreeOfTwoLonlat
    image, jpg_name = gpano.getImagefrmAngle(float(car_lon),float(car_lat), saved_path,yaw=yaw,prefix=panoId)
    url = gpano.getGSV_url_frm_lonlat(float(car_lon),float(car_lat), heading=yaw)
    print("Google street view URL:", url)
    print("PanoID:", panoId)
    # print(image)
    # print(jpg_name)
    # ---------------------------------------------------------------------------

#Tree long lat positions as input


# downloadImg(-75.14474465,39.98868215)

def downloadImgs(lon_lat_list, saved_path):
    while len(lon_lat_list) > 0:
        try:
            lon, lat = lon_lat_list.pop(0)
            downloadImg(lon,lat, saved_path)
        except Exception as e:
            print("Error in downloadImgs():", e)
            continue

def test_downloadImgs_mp(lon_lst_csv= r"K:\OneDrive_NJIT\OneDrive - NJIT\Research\Trees\datasets\NewYorkCity\NYC_Trees20k.csv", saved_path= r"K:\Research\Trees\NewYorkCity_test\google_street_images", Process_cnt = 10):
    print("lon_lst_csv: ", lon_lst_csv)
    lon_lats = pd.read_csv(lon_lst_csv)

    mid = int(len(lon_lats)/2)

    print(len(lon_lats))
    pool = mp.Pool(processes=Process_cnt)
    lon_lats_mp = mp.Manager().list()

    for idx, lonlat in lon_lats[: ].iterrows():
        lon = lonlat['POINT_X']
        lat = lonlat['POINT_Y']
        lon_lats_mp.append((lon, lat))

    for i in range(Process_cnt):
        pool.apply_async(downloadImgs, args=(lon_lats_mp, saved_path))
    pool.close()
    pool.join()

    print("Done.")



def readCSV(n):
    with open(r"K:\OneDrive_NJIT\OneDrive - NJIT\Research\Trees\datasets\NewYorkCity\NYC_Trees20k.csv") as csv_file:
        i = 0
        # csv_reader = csv.reader(csv_file, delimiter=',')
        for row in itertools.islice(csv.DictReader(csv_file), 0,n):

            try:

                print(i, row['POINT_X'], row['POINT_Y'])
                downloadImg(row["POINT_X"],row['POINT_Y'],n)
                # each_row = frozenset(row)
                # data.append(each_row)
                i += 1
            except Exception as e:
                print("Error in downloadImg():", e)

            # for item in each_row:
            #     itemSet.add(frozenset([item]))
# readCSV(19951)


if __name__ == "__main__":
    test_downloadImgs_mp()