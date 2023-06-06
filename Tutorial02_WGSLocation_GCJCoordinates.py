import requests
import json

#1 find all of the hospitals within 2000 meters from the market

YOUR_KEY = 'AIzaSyB_6H9c8l4ABA6quJOWpLxL4ROZZL2bgIY'
BASE_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={0}&location={1}&radius={2}&type={3}&keyword={4}'  


def jsonFormat(res):
  c = dict() # empty dict as container
  for i in res['results']:
  # print(i['name'], i['geometry']['location']['lat'], i['geometry']['location']['lng'])
    c[i['name']] = [float(i['geometry']['location']['lat']), 
                    float(i['geometry']['location']['lng'])]  
  return c
  
   
def nearBySearch(lat, lng, radius, placeType = '', keyword = ''):
  latlng = str(lat) + ',' + str(lng)
  url = BASE_URL.format(YOUR_KEY, latlng, radius, placeType, keyword)
  # print(url)
  response = requests.get(url,timeout=10)
  data = response.json()
  if data['status'] == 'OK':
    return jsonFormat(data)
  else:
    print("error: "+ url)
    return

wh_lat = 30.619779
wh_lng = 114.257871
typecode = 'hospital'
radius_init = 2000

wh_hospital = nearBySearch(wh_lat, wh_lng, radius_init, typecode)
print(wh_hospital)

from math import radians, degrees, sin, cos, asin, acos, sqrt

def great_circle(lon1, lat1, lon2, lat2):
  radius_of_earth = 6371
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  return radius_of_earth * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))

print(great_circle(wh_lng, wh_lat, wh_lng+0.01, wh_lat))

ratio_of_lng_km = 0.01/0.956
ratio_of_lat_km = 0.01/1.11

wh_lat = 30.619779
wh_lng = 114.257871

radius_init = 2000

ratio_of_lng_km = 0.01/0.956
ratio_of_lat_km = 0.01/1.11
radius_init = 2000

def get_sub_center(lat, lng,radius):
  ul_lat = lat + (radius/1000) * ratio_of_lat_km
  ul_lng = lng - (radius/1000) * ratio_of_lng_km
  lr_lat = lat - (radius/1000) * ratio_of_lat_km
  lr_lng = lng + (radius/1000) * ratio_of_lng_km

  result = [
      [(lat + ul_lat)/2, (lng+ul_lng)/2],
      [(lat + ul_lat)/2, (lng+lr_lng)/2],
      [(lat + lr_lat)/2, (lng+ul_lng)/2],
      [(lat + lr_lat)/2, (lng+lr_lng)/2]
  ]
  return result

subcenters = get_sub_center(wh_lat, wh_lng, 2000)
print(subcenters)

for i in get_sub_center(wh_lat, wh_lng, 2000):
  hospital_res = nearBySearch(i[0], i[1], radius_init/(2**0.5), typecode)
  print(len(hospital_res))

lst_box = [
    [wh_lat, wh_lng, radius_init]
]

container = dict()

while lst_box:
  [lat, lng, radius] = lst_box.pop()
  result = nearBySearch(lat, lng, radius*1.05, typecode)
  if result:
    for r in result:
      container[r] = result[r]
    if len(result) >= 20:
      subcenter = get_sub_center(lat,lng, radius)
      for sub in subcenter:
        lst_box.append([sub[0], sub[1], radius/(2**0.5)])

print(container)

print(len(container))

#2 Plot all of the hospital names with their WGS locations on the base map of Gaode and Google satellite map

!pip install folium --user
#basemap url
google_road_map = 'http://mt.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
google_satallite_map = 'http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}'
gaode = 'http://wprd03.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}' 
tencent = 'http://rt1.map.gtimg.com/tile?z={z}&x={x}&y={-y}&styleid=1&version=117'
import folium

map_wh = folium.Map(location = [wh_lat, wh_lng], zoom_start = 14)
folium.TileLayer(tiles=google_satallite_map, attr='Google Satellite', name= 'Google Satellite').add_to(map_wh)
folium.TileLayer(tiles=gaode, attr='高德地图',name = '高德地图').add_to(map_wh)
folium.LayerControl().add_to(map_wh)
for k in container:
  folium.Marker(container[k], tooltip=k, popup=container[k]).add_to(map_wh)

map_wh

#3 Calculate the GCJ coordiantes of those hospitals and plot them on the same map as step2 (don't create new map object)

!pip install coord_convert

from coord_convert.transform import wgs2gcj, gcj2wgs
for location, coordinates in container.items():
    wgs_lat, wgs_lng = coordinates
    gcj_lng, gcj_lat = wgs2gcj(wgs_lng, wgs_lat)   
    folium.Marker([gcj_lat,gcj_lng],icon=folium.Icon(color="red", icon="info-sign")).add_to(map_wh)

map_wh

#4 Link the corresponding hospital among WGS and GCJ coordinates, and plot the link on the same map as step2 (don't create new map object)

for location, coordinates in container.items():
    wgs_lat, wgs_lng = coordinates
    gcj_lng, gcj_lat = wgs2gcj(wgs_lng, wgs_lat)
    points = [[wgs_lat,wgs_lng], [gcj_lat,gcj_lng]]
    # print(points)
    folium.PolyLine(points, color='green', weight = 2).add_to(map_wh)

map_wh
