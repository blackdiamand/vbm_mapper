# Import necessary modules
import matplotlib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopandas.tools import geocode
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from geodatasets import get_path
from tqdm import tqdm
tqdm.pandas()

# Filepath
fp = r"absentee_20241105.csv"

# Read the data
data = pd.read_csv(fp, sep=',', encoding='unicode_escape', converters={i: str for i in range(0, 100)})
#data.fillna('')

#create address string from data
addr_cols = ['ballot_mail_street_address', 'ballot_mail_city', 'ballot_mail_state', 'ballot_mail_zip',
             'other_mail_addr1', 'other_mail_addr2', 'other_city_state_zip']
data['addr'] = data[addr_cols].agg(' '.join, axis=1)
data['addr'] = data['addr'].replace(r'\s+', ' ', regex=True)
data['addr'] = data['addr'].str.strip()

from geopy.geocoders import Photon
geolocator = Photon(user_agent="nc_tracker2", timeout=10)

from geopy.extra.rate_limiter import RateLimiter
geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)
geo = data['addr'].progress_apply(geocoder)
points_df = geo.apply(lambda loc: tuple(loc.point) if loc else None)

points = [Point(coord[1], coord[0]) if coord else None for coord in points_df]

world = gpd.read_file(r'ne_110m_land/ne_110m_land.shp')
gdf = gpd.GeoDataFrame(
    data, geometry=points
)
ax = world.plot()
gdf.plot(ax=ax, markersize=0.1, color='r', marker=',', alpha=0.1)
from matplotlib import pyplot
#pyplot.show()
pyplot.savefig('out.png', dpi=1000)