import requests
import pandas as pd

#1 Find the coordinate of Tsim Sha Tsui Station
def getGeoCoord(address,key):
  base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
  url = base_url+'address='+address.replace(' ', '+')+'&key='+API_KEY
  response = requests.get(url,timeout=10)
  data = response.json()
  if data['status'] == 'OK':
    result = data['results'][0]
    location = result['geometry']['location']
    return location['lat'], location['lng']
  else:
    print("error: "+address)
    return

API_KEY = 'AIzaSyB_6H9c8l4ABA6quJOWpLxL4ROZZL2bgIY'
address = 'Tsim Sha Tsui Station'

ll=getGeoCoord(address,API_KEY)
Tism_lat=ll[0]
Tism_lng=ll[1]

#2 Find all coordinates of the addresses in Wellcome website and upload data in Colab
add = []
coor = []


with open('/content/WellcomeStore_Updated_2023.csv','r') as infile:
  for line in infile:
    add.append(line)
    add.append(getGeoCoord(line,API_KEY))


#3 get lat lng    
from pandas.core.frame import DataFrame
coor_clean=DataFrame(add)#以行为标准写入

coor_clean1=coor_clean[coor_clean.index%2==0]  #保留奇数行
coor_clean1 = coor_clean1.reset_index(drop=True)
coor_clean2=coor_clean[coor_clean.index%2==1]  #保留偶数行
coor_clean2 = coor_clean2.reset_index(drop=True)
coor_clean0 = pd.merge(coor_clean1,coor_clean2,how='inner',left_index=True,right_index=True)

coor_clean_r = coor_clean0.dropna(how='any', axis=0, subset=["0_y"] ,inplace=False)
coor_clean_r['0_y'] = coor_clean_r['0_y'].apply(str)
coor_clean_r['long'], coor_clean_r['lat'] = coor_clean_r['0_y'].str.split(',', 1).str
coor_clean_r['long'] = coor_clean_r['long'].str.strip('(')
coor_clean_r['lat'] = coor_clean_r['lat'].str.strip(')')
coor_final=coor_clean_r.rename(columns={"0_x": "0", "0_y": "1", "long": "3", "lat": "4"})
#print(coor_final)
coor_final.to_csv('/content/WellcomeStore_cleaned.csv')

#4 find stores within 1km
# Haversine formula, distance between two coordinates
from math import radians, degrees, sin, cos, asin, acos, sqrt

def great_circle(lon1, lat1, lon2, lat2):
  radius_of_earth = 6371
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  return radius_of_earth * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))

import csv
with open('/content/WellcomeStore_cleaned.csv','r') as infile:
  reader = csv.reader(infile)
  count = 0
  row = 1  
  for row in reader:
    distance = great_circle(Tism_lng,Tism_lat,float(row[4]),float(row[3]))
    if distance<=1:
      count = count+1
      print(f'Distance: {distance}km{row[2]}\n Address: {row[1]}')
  print(count)