#1. Generate clusters for shared bike data and find the center of each cluster

!pip install sklearn # an important machine learning package
import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
!pip install folium
import folium
from sklearn.cluster import DBSCAN

# load a mobike data in Shanghai
mobike_df = pd.read_csv('https://github.com/gyshion/tutorial/raw/main/mobike_shanghai1.csv')

# stack the origin points with destination points  &&&  all of points
new_ll = []

for index, row in mobike_df.iterrows():
    new_ll.append([row['start_location_y'],row['start_location_x']])
    new_ll.append([row['end_location_y'],row['end_location_x']])

all_pt =pd.DataFrame(data = new_ll, columns = ["y", "x"]) 

# train the model
db_mobike = DBSCAN(eps = 0.0005, # ~ 50 meter
                   min_samples = 20).fit(all_pt[['y','x']])

predict_mobike = db_mobike.fit_predict(all_pt[['y','x']]) # predict by the model
all_pt['label'] = predict_mobike

# assign the cluster to OD points
mobike_df['start_cluster'] = db_mobike.fit_predict(mobike_df[['start_location_y','start_location_x']]) # predict by the model
mobike_df['end_cluster'] = db_mobike.fit_predict(mobike_df[['end_location_y','end_location_x']]) # predict by the model

# filter only the od among clusters
mobike_df_cluster = mobike_df.query("start_cluster>=0 and end_cluster>=0")

#create new columns to put the center points of each clusters(for the same label)
mobike_df_cluster.insert(mobike_df_cluster.shape[1],'center_startX',0)
mobike_df_cluster.insert(mobike_df_cluster.shape[1],'center_startY',0)

#for start locations X,Y
NEW_mobike_df_cluster = pd.DataFrame()

for i in range(mobike_df_cluster['start_cluster'].max()+1):
  try:
    center_startX = mobike_df_cluster[mobike_df_cluster['start_cluster']==i]['start_location_x'].mean()
    center_startY = mobike_df_cluster[mobike_df_cluster['start_cluster']==i]['start_location_y'].mean()
    temp = mobike_df_cluster[mobike_df_cluster['start_cluster']==i]
    temp['center_startX']=center_startX
    temp['center_startY']=center_startY
    NEW_mobike_df_cluster = NEW_mobike_df_cluster.append(temp)
  except:
    pass


#create new columns to put the center points of each clusters(for the same label)
NEW_mobike_df_cluster.insert(NEW_mobike_df_cluster.shape[1],'center_endX',0)
NEW_mobike_df_cluster.insert(NEW_mobike_df_cluster.shape[1],'center_endY',0)
NEW_mobike_df_cluster

#for start locations X,Y
Final_mobike_df_cluster = pd.DataFrame()

for i in range(NEW_mobike_df_cluster['end_cluster'].max()+1):
  try:
    center_endX = NEW_mobike_df_cluster[NEW_mobike_df_cluster['end_cluster']==i]['end_location_x'].mean()
    center_endY = NEW_mobike_df_cluster[NEW_mobike_df_cluster['end_cluster']==i]['end_location_y'].mean()
    temp = NEW_mobike_df_cluster[NEW_mobike_df_cluster['end_cluster']==i]
    temp['center_endX']=center_endX
    temp['center_endY']=center_endY
    Final_mobike_df_cluster = Final_mobike_df_cluster.append(temp)
  except:
    pass

#delete the orignal data and get the columns which contains the start/end clusters and start/end center points 
mobike_df_center = Final_mobike_df_cluster.loc[:,['orderid','start_cluster','end_cluster','center_startX','center_startY','center_endX','center_endY']]

#groupby the dataframe, and get the counts of each od pair
df_counts = mobike_df_center.groupby(["start_cluster","end_cluster"])['orderid'].count().rename('count').reset_index()
mobike_clusterCenter = pd.merge(df_counts, mobike_df_center, how= "left" )

#delete the duplicated rows which contains the same start/end cluster id
mobike_clusterCenter = mobike_clusterCenter.drop_duplicates(['start_cluster','end_cluster'])

#get the count(od pair weight) of each center
mobike_clusterCenter

#2. Create network from shared bike data

!pip install networkx --user # most important network module
!pip install matplotlib --user
import networkx as nx
import matplotlib

# import the data into a new network

G_bike=nx.Graph() 

pos_bike = dict() #store the location of airports

for index, row in mobike_clusterCenter.iterrows():
    if row['count']>0:  # import the data with more numbers of 1
        start = str(row['center_startY'])+','+str(row['center_startX'])
        end = str(row['center_endY'])+','+str(row['center_endX'])
        G_bike.add_edge(start,end,weight=row['count'])
        pos_bike[start] = [row['center_startX'],row['center_startY']]
        pos_bike[end] = [row['center_endX'],row['center_endY']]

nx.draw(G_bike,pos=pos_bike,node_size=40)

#3. Use network analysis on the shared bike network

# calculate the eigenvector_centrality
eigenvector_centrality_map = nx.algorithms.centrality.eigenvector_centrality(G_bike,weight='count')  # betweenness centrality in next step
print(eigenvector_centrality_map)

nx.draw(G_bike,pos=pos_bike,node_size=30,node_color=list(eigenvector_centrality_map.values()))

gaode = 'http://wprd03.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}' 
sh_lat = 31.22 
sh_lng = 121.46

# todo: plot the data on the folium map
map_bikes = folium.Map(location=[sh_lat,sh_lng],tiles=gaode,attr='test',zoom_start=11)

for k in eigenvector_centrality_map:
  lnglat = k.split(',')
  folium.Circle(
      [float(lnglat[0]),float(lnglat[1])],
      radius = eigenvector_centrality_map[k]*8000,
      #color = random_color(row['label']),
      #radius=3,
      fill=True
  ).add_to(map_bikes)

map_bikes

#flow: represent the count of each OD pair which derived from the start cluster numbers and the end cluster numbers. 
#So the weight in the network analysis is the number of count that means the bike flow numbers(real OD numbers) from the start point to the ened points.
#result: This map shows the OD-pair numbers of the center points in Shanghai. So the start points and end points of mobike usage are dense in the Huangpu District,Xuhui District,Yangpu District.