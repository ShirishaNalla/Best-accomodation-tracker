import json   
import pandas as pd  
import requests
from tabulate import tabulate
from sklearn.cluster import KMeans
import random
import numpy as np
import pandas as pd
import folium


#Fetching data from HERE API for JNTUH College
url = 'https://discover.search.hereapi.com/v1/discover?in=circle:17.4933,78.3914;r=10000&q=apartment&apiKey=7lUjRE6o5Cf4xhmetS6ljNw4mIBo0yPO1zhLpbMVFYI'
data = requests.get(url).json()
data=pd.json_normalize(data['items'])

#Cleaning API data
data=data[['title','address.label','distance','access','position.lat','position.lng','address.postalCode','id']]
data.to_csv('apartment.csv')

#Counting no. of cafes, department stores and gyms near apartments around JNTUH College
data_final=data[['position.lat','position.lng']]

CafeList=[]
DepList=[]
GymList=[]
latitudes = list(data['position.lat'])
longitudes = list( data['position.lng'])

for lat, lng in zip(latitudes, longitudes):    
    radius = '1000' #Set the radius to 1000 metres
    
    search_query = 'cafe' #Search for any cafes
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=7lUjRE6o5Cf4xhmetS6ljNw4mIBo0yPO1zhLpbMVFYI'.format(lat, lng, radius, search_query)
    results = requests.get(url).json()
    venues=pd.json_normalize(results['items'])
    CafeList.append(venues['title'].count())
	
    search_query = 'gym' #Search for any gyms
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=7lUjRE6o5Cf4xhmetS6ljNw4mIBo0yPO1zhLpbMVFYI'.format(lat, lng, radius, search_query)
    results = requests.get(url).json()
    venues=pd.json_normalize(results['items'])
    GymList.append(venues['title'].count())

    search_query = 'department-store' #search for supermarkets
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=7lUjRE6o5Cf4xhmetS6ljNw4mIBo0yPO1zhLpbMVFYI'.format(lat, lng, radius, search_query)
    results = requests.get(url).json()
    venues=pd.json_normalize(results['items'])
    DepList.append(venues['title'].count())

data_final['Cafes'] = CafeList
data_final['Department Stores'] = DepList
data_final['Gyms'] = GymList

print(tabulate(data_final,headers='keys',tablefmt='github'))



#Run K-means clustering on dataframe
kclusters = 3

kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(data_final)
data_final['Cluster']=kmeans.labels_
data_final['Cluster']=data_final['Cluster'].apply(str)

print(tabulate(data_final,headers='keys',tablefmt='github'))



#Plotting clustered locations on map using Folium

#define coordinates of the college
res_map=folium.Map(location=[17.4933,78.3914],zoom_start=14)

# instantiate a feature group for the incidents in the dataframe
locations = folium.map.FeatureGroup()

# set color scheme for the clusters
def color_producer(cluster):
    if cluster=='2':
        return 'green'   #more Cafes,Department stores,Gyms
    elif cluster=='1':
        return 'orange'  #less Cafes,medium Department stores ,more Gyms
    else:
        return 'red'  # medium Cafes,Department stores,Gyms 

latitudes = list(data_final['position.lat'])
longitudes = list(data_final['position.lng'])
labels = list(data_final['Cluster'])
names=list(data['title'])
for lat, lng, label,names in zip(latitudes, longitudes, labels,names):
    folium.CircleMarker(
            [lat,lng],
            fill=True,
            fill_opacity=1,
            popup=folium.Popup(names, max_width = 300),
            radius=5,
            color=color_producer(label)
        ).add_to(res_map)

# add locations to map
res_map.add_child(locations)
folium.Marker([17.4933,78.3914],popup='JNTUH College').add_to(res_map)

#saving the map 
res_map.save("JNTUHmap.html")
