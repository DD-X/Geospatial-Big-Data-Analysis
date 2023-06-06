#read data
import pandas as pd
k_df = pd.read_csv('https://raw.githubusercontent.com/gyshion/tutorial/main/K.csv')
#print("k_df' size: ",len(k_df))

m_df = pd.read_csv('https://raw.githubusercontent.com/gyshion/tutorial/main/M.csv')
#print("M_df' size: ",len(m_df))

food_df = pd.read_csv('https://github.com/gyshion/tutorial/raw/main/restaurants.zip')
#print("food_df' size: ",len(food_df))

!pip install h3
import h3

#define the levels
k_df['h3lv4']= k_df.apply(lambda row: h3.geo_to_h3(row['y'],row['x'],4),axis=1)
m_df['h3lv4']= m_df.apply(lambda row: h3.geo_to_h3(row['y'],row['x'],4),axis=1)

k_df['h3lv7']=k_df.apply(lambda row: h3.geo_to_h3(row['y'],row['x'],7),axis=1)
food_df['h3lv7']=food_df.apply(lambda row: h3.geo_to_h3(row['y'],row['x'],7),axis=1)

m_h3_lst=m_df.groupby(['h3lv4']).apply(lambda df:list(zip(df.y,df.x))).to_dict()
food_h3_lst=food_df.groupby(['h3lv7']).apply(lambda df:list(zip(df.y,df.x))).to_dict()

!pip install haversine
import haversine
import numpy as np
from haversine import haversine_vector,Unit

def count_within_dist(py,px,list_of_coor,min_dist):
  dist_matrix = haversine_vector([py,px],list_of_coor,Unit.KILOMETERS,comb=True)
  return np.sum(dist_matrix<=min_dist) #min dist of all the distance

def min_dist_of_point_2_list_of_points(py,px,list_of_coor):
  dist_matrix=haversine_vector([py,px],list_of_coor,Unit.KILOMETERS,comb=True)
  return np.min(dist_matrix)#min dist of all the distances

output_lst = []
for index,row in k_df.iterrows():
  #print(row)

  #m stores
  h3lv4s=h3.k_ring(row['h3lv4'],1) #find the neibor h3
  current_m_lst=[] #store all m store near the current k store
  for h3_code in h3lv4s:
    if h3_code in m_h3_lst:
      current_m_lst += m_h3_lst[h3_code]
  
  #other food stores
  h3lv7s=h3.k_ring(row['h3lv7'],1)
  current_food_lst=[]
  for h3_code in h3lv7s:
    if h3_code in food_h3_lst:
      current_food_lst += food_h3_lst[h3_code]

  #No exisiting M stores within 10km
  condition1 = 0
  if len(current_m_lst)==0:
    condition1 = 1
  else:
    min_dist=min_dist_of_point_2_list_of_points(row['y'],row['x'],current_m_lst)
    if min_dist>10: #the nearest M is 10km far away
      condition1=1
  
  #More than 100 other food stores within 500m
  condition2=0
  if len(current_food_lst)==0:#no other food store nearby
    #print(len(current_food_lst))
    condition2=0
  else:
    num_of_other_food = count_within_dist(row['y'],row['x'],current_food_lst,0.5)
    #print(num_of_other_food)
    if num_of_other_food>100:
      condition2=1

  #combine two conditions
  if condition1+condition2==2:
    #print(row['x'],row['y'])
    output_lst.append((row['x'],row['y']))


print(output_lst)