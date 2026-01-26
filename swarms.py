"""
This module contains a function that groups earthquakes into swarms.

Please see Examples.ipynb for help with importing the module and calling
the function find_swarms().
"""

from datetime import datetime
from collections import namedtuple

import pandas as pd
from geopy import distance


def find_swarms(eq_df,
                time_lim = 50,  # hours
                dist_lim = 50,  # km
                min_number = 2,
                time_col = "time",
                lat_col = "latitude",
                lon_col = "longitude",
                mag_col = "mag"):
    """
    Group earthquakes into swarms and record swarm properties.
    
    Parameters
    ----------
    eq_df : pandas DataFrame
        DataFrame of earthquake data. Must have columns for origin time,
        latitude, longitude, and magnitude.
    time_lim : int or float, default 50
        Maximum time interval (in hours) between any given earthquake and
        the preceding earthquake in the same swarm.
    dist_lim : int or float, default 50
        Maximum distance interval (in kilometres) between any given
        earthquake and the nearest (in space) preceding earthquake in the
        same swarm.
    min_number : int, default 2
        Minimum number of earthquakes required to be grouped together to be
        considered a swarm.
    time_col : int or str, default "time"
        Label for the DataFrame column in which values are timezone-aware
        datetime objects representing origin times. If an integer is given,
        it must correspond to the label, not the integer position along the
        index.
    lat_col : int or str, default "latitude"
        Label for the DataFrame column in which values are integers or
        floats representing latitudes. If an integer is given, it must
        correspond to the label, not the integer position along the index.
    lon_col : int or str, default "longitude"
        Label for the DataFrame column in which values are integers or
        floats representing longitudes. If an integer is given, it must
        correspond to the label, not the integer position along the index.
    mag_col : int or str, default "mag"
        Label for the DataFrame column in which values are integers or
        floats or None representing magnitudes. If an integer is given, it
        must correspond to the label, not the integer position along the
        index.
    
    Returns
    -------
    A named tuple of DataFrames. Field name "swarms" corresponds to a
    DataFrame of swarms and their properties, "quakes" corresponds to
    a DataFrame of all input earthquakes with an ID indicating the swarm
    to which they belong.
    
    Notes
    -----
    Please see Examples.ipynb for help with calling this function.
    
    """
    
    # Prevent inaccuracies due to times lacking dates and datetimes
    # lacking time zones
    for t in eq_df[time_col]:
        if not isinstance(t, datetime):
            raise TypeError(
                "values in DataFrame column %s must be 'datetime' type objects, not '%s'" 
                %(repr(time_col), type(t).__name__))
        if (t.tzinfo is None) or (t.tzinfo.utcoffset(t) is None): 
            raise ValueError("'datetime' objects must be timezone-aware")
    
    eq_df = eq_df.sort_values(by=time_col)
    eq_df.index = range(len(eq_df))
    
    # Create columns for swarm properties
    start_time = []
    end_time = []
    first_lat = []
    first_lon = []
    centre_lat = []
    centre_lon = []
    eq_count = []
    duration = []
    mag_seq = []
    t_seq = []
    d_seq = []
    t_max = []
    d_max = []
    t_avg = []
    d_avg = []
    indxes = []
    
    # Create flat list for indices of all earthquakes included in swarms
    in_swarm = []
    
    # Go through each earthquake as a potential first earthquake in a swarm
    for i in eq_df.index[:-1]:
        if i in in_swarm:
            continue
        # Collect data on earthquakes in each swarm, recycled for each swarm
        time = []
        lat = []
        lon = []
        mag = []
        t_intervals = []
        d_intervals = []
        indx = []
        count = 1
        time.append(eq_df[time_col].iloc[i])
        lat.append(eq_df[lat_col].iloc[i])
        lon.append(eq_df[lon_col].iloc[i])
        mag.append(eq_df[mag_col].iloc[i])
        indx.append(i)
        
        in_swarm.append(i)
        
        # Check earthquakes to include in swarm with first earthquake i
        for j in eq_df.index[i+1:]:
            if j in in_swarm:
                continue
            # Check time between previous earthquake in swarm and earthquake j
            time_j = eq_df[time_col].iloc[j]
            time_p = eq_df[time_col].iloc[in_swarm[-1]]
            time_interval = ((time_j - time_p).total_seconds()/3600)
            if time_interval > time_lim:
                break
            # Check geodesic distance between earthquake j and nearest previous 
            # earthquake in swarm
            point_j = (eq_df[lat_col].iloc[j], eq_df[lon_col].iloc[j])  
            dist_jk = []
            for k in in_swarm[-count:]:
                point_k = (eq_df[lat_col].iloc[k], eq_df[lon_col].iloc[k])
                dist_diff = distance.distance(point_j, point_k).km  
                dist_jk.append(dist_diff)
            dist_interval = min(dist_jk)
            if dist_interval <= dist_lim:
                time.append(eq_df[time_col].iloc[j])
                lat.append(eq_df[lat_col].iloc[j])
                lon.append(eq_df[lon_col].iloc[j])
                mag.append(eq_df[mag_col].iloc[j])
                t_intervals.append(time_interval)
                d_intervals.append(dist_interval)
                indx.append(j)
                in_swarm.append(j)
                count += 1
        
        # Collect current swarm's info
        # unless too few earthquakes are grouped together
        if count < min_number:
            in_swarm = in_swarm[:-count]
            continue
        start_time.append(time[0])
        end_time.append(time[-1])
        first_lat.append(lat[0])
        first_lon.append(lon[0])
        centre_lat.append((max(lat)+min(lat)) / 2)
        centre_lon.append((max(lon)+min(lon)) / 2)
        eq_count.append(count)
        duration.append(time[-1] - time[0])
        mag_seq.append(mag)
        t_seq.append(t_intervals)
        d_seq.append(d_intervals)
        t_max.append(max(t_intervals))
        d_max.append(max(d_intervals))
        t_avg.append(sum(t_intervals)/len(t_intervals))
        d_avg.append(sum(d_intervals)/len(d_intervals))
        indxes.append(indx)
    
    swarm_df = pd.DataFrame({
        "Swarm ID": list(range(len(start_time))),
        "Start Time": start_time,
        "End Time": end_time,
        "Duration": duration,
        "Origin Latitude": first_lat,
        "Origin Longitude": first_lon,
        "Centre Latitude": centre_lat,
        "Centre Longitude": centre_lon,
        "Number of Earthquakes": eq_count,
        "Magnitudes": mag_seq,
        "Time Intervals (h)": t_seq,
        "Distance Intervals (km)": d_seq,
        "Minimum Time Limit (h)": t_max,
        "Minimum Distance Limit (km)": d_max,
        "Average Time Interval (h)": t_avg,
        "Average Distance Interval (km)": d_avg
    })
    
    # Assign swarm ID to each earthquake in a swarm
    swarm_id = pd.Series(index=range(len(eq_df)), dtype="Int64")
    for swarm in range(len(indxes)):
        for eq in indxes[swarm]:
            swarm_id[eq] = swarm
    eq_df.insert(loc=0, column="Swarm ID", value=swarm_id)
    
    Output = namedtuple("Output", ["swarms", "quakes"])
    
    return Output(swarms=swarm_df, quakes=eq_df)