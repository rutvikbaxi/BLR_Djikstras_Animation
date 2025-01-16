import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import plotly.graph_objects as go
import math

shapefile_path = "roadl_ind.shp"  
roads = gpd.read_file(shapefile_path)

G = nx.Graph()
for _, row in roads.iterrows():
    
    line = row.geometry
    if line.geom_type == "LineString":
        coords = list(line.coords)
        for i in range(len(coords) - 1):
            G.add_edge(
                (coords[i][0], coords[i][1]),
                (coords[i + 1][0], coords[i + 1][1]),
                weight=line.length
            )
        
start_coord = (77.44, 12.82) 
end_coord = (77.74, 13.43)

center_lat = (start_coord[1] + end_coord[1]) / 2
center_long = (start_coord[0] + end_coord[0]) / 2

# Define the bounding box
min_lat = min(start_coord[1], end_coord[1]) - 0.05
max_lat = max(start_coord[1], end_coord[1]) + 0.05
min_long = min(start_coord[0], end_coord[0]) - 0.05
max_long = max(start_coord[0], end_coord[0])   + 0.05

G_filtered = nx.Graph()
for u, v, data in G.edges(data=True):
    if (min_long <= u[0] <= max_long and min_lat <= u[1] <= max_lat and
        min_long <= v[0] <= max_long and min_lat <= v[1] <= max_lat):
        G_filtered.add_edge(u, v, **data)
G = G_filtered

def euclidean_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def find_nearest_node(G, target_coord):
    nearest_node = None
    min_distance = float('inf')
    
    for node in G.nodes:
        distance = euclidean_distance(target_coord, node)
        
        if distance < min_distance:
            min_distance = distance
            nearest_node = node
    
    return nearest_node

start2_coord = ( 77.62392288828865, 12.911772219885378)

start_node = find_nearest_node(G, start2_coord)
end_node = find_nearest_node(G, end_coord)

print(f"Start Node: {start_node}")
print(f"End Node: {end_node}")

# Compute the shortest path
shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")

fig = go.Figure()

fig.update_layout(
    mapbox=dict(
        style="open-street-map",  # OpenStreetMap style
        center=dict(lat=center_lat, lon=center_long),  # Center on India
        zoom=9, 
    ),
    showlegend=False,
)

edge_lines = []

for edge in G.edges(data=True):
    x0, y0 = edge[0]  # Start coordinates of the edge
    x1, y1 = edge[1]  # End coordinates of the edge

    edge_lines.append(dict(
        type="scattermapbox",
        lon=[x0, x1],  # Longitude coordinates
        lat=[y0, y1],  # Latitude coordinates
        mode="lines",
        line=dict(width=1.5, color="#02662c"),  # Line style
    ))


for line in edge_lines[:500]:
    fig.add_trace(go.Scattermapbox(
        lon=line['lon'],
        lat=line['lat'],
        mode=line['mode'],
        line=line['line'],
    ))

print("added edges")
frames = []
path_x, path_y = [], []

print("Leng of shortest path", len(shortest_path))
print("Length of Graph", len(edge_lines))

for i in range(len(shortest_path) - 1):
    path_x += [shortest_path[i][0], shortest_path[i + 1][0], None]
    path_y += [shortest_path[i][1], shortest_path[i + 1][1], None]

    # Add a frame for the current segment
    frames.append(
        go.Frame(
            data=[
                go.Scattermapbox(
                    lat=path_y,
                    lon=path_x,
                    mode="lines",
                    line=dict(color="#02662c", width=4),
                    name="Shortest Path",
                )
            ]
        )
    )

fig.frames = frames

fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="Play",
                    method="animate",
                    args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)],
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[[None], dict(frame=dict(duration=0, redraw=False))],
                ),
            ],
        )
    ]
)

fig.show()
