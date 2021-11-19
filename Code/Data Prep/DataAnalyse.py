"Data Analyse: first impression and some key facts"

path = r'C:\Users\Danie\Simpy Master\Data Prep'         # Set the path of the folder where the data is located


import pandas as pd                                     # Pandas offers tools for the management of data and their analysis.

data = pd.read_csv('outputCTMar.csv')                   # Import all arrivals of China Town in march



print('China Town parking spaces = %d' %(data['DeviceId'].nunique()))   # Count all sensors by just filtering through unique sensors

index = data.index                                      # Determination of the index
number_of_arrivals = len(index)                         # Count the number of arrivals in March


print('China Town arrivals in Mar = %d'  % (number_of_arrivals))

print ('China Town mean parking duration = %d' % (data['DurationMinutes'].mean()))  # Determination of the mean parking duration


print ("finished")      