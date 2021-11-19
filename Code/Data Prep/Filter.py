"First filter of the whole Data Set"

path = r'C:\Users\Danie\Simpy Master\Data Prep'             # Set the path of the folder where the data is located


import pandas as pd                                         # Pandas offers tools for the management of data and their analysis.

# Only read the relevant columns from the data set
data = pd.read_csv('Car.csv', usecols= ['DeviceId','ArrivalTime', 'DepartureTime', 'DurationMinutes', 'AreaName', 'BayId'])


data = data[data['AreaName'] == 'China Twon']               # Filter the new Data Set for the area China Town

data.to_csv('outputCT.csv')                                 # Create a new CSV File 


print ("finished")
