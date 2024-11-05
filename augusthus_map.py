import pandas as pd
import folium
from folium import plugins
from folium.plugins import AntPath
from geopy.distance import geodesic
import numpy as np
from sklearn.cluster import DBSCAN


#Opsætning
destination_address = "Amagerfælledvej 106" #Destinationsadresse
max_radius = 6000 # max radius i meter
map_center = [55.6562264, 12.591784] #centrum punkt for display
df = pd.read_excel('augusthus_data_processed.xlsx') # data load


filtered_df = df[df['new_address'].str.contains(destination_address, case=False, na=False)]
m = folium.Map(location=map_center, zoom_start=14)
old_coords = filtered_df[['from_lat', 'from_lon']].values
db = DBSCAN(eps=0.005, min_samples=2).fit(old_coords)
labels = db.labels_

unique_labels, counts = np.unique(labels[labels != -1], return_counts=True)
if unique_labels.size > 0:
    densest_cluster_label = unique_labels[np.argmax(counts)]
    densest_cluster_points = old_coords[labels == densest_cluster_label]

    best_center = densest_cluster_points.mean(axis=0)

    folium.Circle(
        location=[best_center[0], best_center[1]],
        radius=max_radius,
        color='green',
        fill=True,
        fill_opacity=0.2,
        popup=f"Target zone to include most companies within a ({max_radius:.2f} meters radius)"
    ).add_to(m)
else:
    print("No valid cluster found for old addresses.")


for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['from_lat'], row['from_lon']],
        popup=f"<b>From:</b> {row['old_address']}<br><b>Company:</b> {row['name']}<br><b>Date:</b> {row['date_of_move']}",
        icon=folium.Icon(icon='home', color='blue')
    ).add_to(m)
   
    AntPath(
        locations=[
            [row['from_lat'], row['from_lon']],
            [row['to_lat'], row['to_lon']]
        ],
        color='black',
        weight=2,
        opacity=0.8,
        delay=1000  
    ).add_to(m)

folium.Marker(
    location=[55.6562264, 12.591784],
    popup=f"<b>Augusthus</b>",
    icon=folium.Icon(icon='home', color='black')
).add_to(m)
m.save('augusthus_target_area.html')


