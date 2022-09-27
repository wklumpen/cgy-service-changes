import datetime
import time
import pandas as pd
import geopandas as gpd 
from r5py import TransportNetwork, TravelTimeMatrixComputer, TransitMode, LegMode


print("Loading Points")
centroids = gpd.read_file("../data/cgy_service_changes.gpkg", layer='hex_centroids')
print(f"There are {centroids.shape[0]} centroids")

print("Loading Runs to Execute")
runs = pd.read_csv('../data/run_reference.csv')
runs['datetime'] = pd.to_datetime(runs['datetime'])
print(f"This will generate {runs.shape[0]} matrices.")
gtfs_file = 'none'
for idx, row in runs.iloc[5:].iterrows():
    print(f"Running {row['matrix_id']}:", row['datetime'])
    new_gtfs_file = f"../data/gtfs/cgy_gtfs_{row['gtfs_feed']}.zip"
    if new_gtfs_file != gtfs_file:
        gtfs_file = new_gtfs_file
        #Setup the network
        print("Setting Up New Network")
        transport_network = TransportNetwork(
            "../data/Calgary.osm.pbf",
            [
                gtfs_file
            ]
        )
    
    # Parse the datetime into appropriate dateime format
    run_time = datetime.datetime(
        year=row['datetime'].year,
        month=row['datetime'].month,
        day=row['datetime'].day,
        hour=row['datetime'].hour
    )
    print("Initializing Matrix Computer")
    travel_time_matrix_computer = TravelTimeMatrixComputer(
        transport_network,
        origins=centroids,
        destinations=centroids,
        departure=run_time,
        departure_time_window=datetime.timedelta(hours=2),
        transport_modes=[TransitMode.TRANSIT, LegMode.WALK]
    )

    print("Computing Travel Times")
    t0 = time.time()
    travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
    t1 = time.time()
    print("Ran in", t1 - t0, "seconds")

    # Write to file
    travel_time_matrix.to_csv(f"../data/matrices/{row['matrix_id']}_{row['gtfs_feed']}.csv", index=False)