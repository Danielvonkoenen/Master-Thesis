"""
Simulation of a Parking lot with charging stations and PV systems



Scenario:
  A parking lot has a limited number of charging stations and PV systems. 
  The charging stations always use the generated PV energy first before accessing the power grid. 

"""


"import relevant library"
import itertools                  # Functional tools for creating and using iterators. 
import random                     # Random variable generators.
import collections                # This module implements specialized container datatypes providing alternatives to Python's general purpose built-in containers, dict, list, set, and tuple.
import pandas as pd               # Pandas offers tools for the management of data and their analysis.

import simpy                      # Simulation Environment

"Scenario / Environment Properties"
SIM_TIME = 86400                  # Simulation time in seconds

#Parking Spaces Properties
NORMAL_SPACES = 35                # Amount of normal parking Spaces

#PV Properties
PV_COUNT = 3                      # Amount of PVs with 1 killowatt-peak equals 4 to 6 moduls, which together occupy a area of 8 to 10 square meters.
PV_GENERATION = 0.4               # PV Generation per 1 hour  - approx. 7 hours sunlight 1 killowatt-peak approx. 1,000 kw per year / 365 /7 = 0.4; Later weather dependent
PV_STORE = 3                      # Max Energy a PV Generator can store kwh

#Charging Stations Properties
CS_COUNT_1 = 0                    # Amount of Charging Stations Level 1
CS_COUNT_2 = 0                    # Amount of Charging Stations Level 2
CS_SPEED_1 = 19.2                 # Charging Speed - Level 2
CS_SPEED_2 = 80                   # Charging Speed - Level 3 DC

#Car Properties
BATTERY_SIZE = [30, 100]          # Min von 30 kw/h - Max 100 kw/h
BATTERY_LEVEL = [5, 99]           # Min/max levels of battery level (in volt)
TIME_OF_STAY = [300,2000]         # Min/max duration of a car parking
CHARGING_PROBABILITY = [1,100]    # Percentage of an EV owner probabilty of charging his EV
EV_ADOPTION = 25                  # Percentage of EV Adoption




"A car arrives at the parking loot."
def arrival(name, env, parking_loot, car_type, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2, chargerAuslastung):
    """
    If the car is an EV it tries to request the charging process.
    If the car is a normal vehicle it tries to request the parking process.
    
    """

    
    print('%s arriving at parking loot at %.1f' % (name, env.now))          # A vehicle enters the parking loot 
    with parking_loot.request() as req:                                     
        start = env.now                                                     # Timestamp of the arrival
        
        yield req                                                           # Ressource solt is requested
        

        "normal vehicle process"

        if car_type == 1:                                                   # Identify a normal vehicle
          if(not ChargingStation.available[p_space]):                       # Check if a normal praking space is free
            print('There is no free parking spot for %s and it can not park at a charging station.' % p_space)
            return                                                          # No parking spot is available / The EV leaves the parking loot
          else:
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return                                                          # The parking process was triggerd 

          
        

        "EV process Level 1 Preference"

        if p_space == 'Level 1':                                            # Check charger Level preference
          if not ChargingStation.availableL1[p_space]:                      # Check charger availability
           print('There is no free parking spot for %s' % p_space)     
          else:
            yield req                                                       # Ressource solt is requested
            yield env.process(charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2))
            return                                                          # The charging process was triggerd

          if not ChargingStation.availableL2[p_space]:                      # Check availability of the second charger Level preference
            print('There is no free parking spot for Level 2')    
          else:
            yield env.process(charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2, chargerAuslastung))
            return                                                          # The charging process was triggerd

          if not ChargingStation.available[p_space]:                        # Check if at least a normal parking space is free
            print('There is no free parking spot for %s ' % name)   

            # Set Up the properties of the EV for the Home Charging consumption
            battery_capacity = random.randint(*BATTERY_SIZE)                
            battery_level = random.randint(5,battery_capacity-1)
            power_required = battery_capacity - battery_level

            # Track the requiered energy for the EV at home
            home_charg.put(power_required + random.randint(5,battery_level))
            item = (env.now, power_required + random.randint(5,battery_level)) 
            export_data.append(item)
            return
          else:                                                             # Nomal parking spot is available
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return                                                          # Parking process was triggered                               
          



        "EV process Level 2 Preference"

        if p_space == 'Level 2':                                            # Check charger Level preference
          if not ChargingStation.availableL2[p_space]:                      # Check charger availability
           print('There is no free parking spot for %s' % p_space)     
          else:
            yield env.process(charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2, chargerAuslastung))
            return                                                          # The charging process was triggerd

          if not ChargingStation.availableL1[p_space]:                      # Check availability of the second charger Level preference
            print('There is no free parking spot for Level 1')    
          else:
            yield env.process(charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2))
            return                                                          # The charging process was triggerd

          if not ChargingStation.available[p_space]:                        # Check if at least a normal parking space is free
            print('There is no free parking spot for %s ' % name)

            # Set Up the properties of the EV for the Home Charging consumption
            battery_capacity = random.randint(*BATTERY_SIZE)
            battery_level = random.randint(5,battery_capacity-1)
            power_required = battery_capacity - battery_level

            # Track the requiered energy for the EV at home
            home_charg.put(power_required + random.randint(5,battery_level))
            item = (env.now, power_required + random.randint(5,battery_level)) 
            export_data.append(item)
            return
          else:                                                             # Nomal parking spot is available
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return                                                          # Parking process was triggered 


        return

"A EV charges at a Level 1 Charging Station"
def charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2):

      # Set Up of the EV and the Charger
      start = env.now
      battery_capacity = random.randint(*BATTERY_SIZE)
      battery_level = random.randint(5,battery_capacity-1)
      parking_time = random.randint(*TIME_OF_STAY)
      charge_preference = random.randint(*CHARGING_PROBABILITY)
      power_required = battery_capacity - battery_level               
      power_possible = CS_SPEED_1 * parking_time
      if power_possible >= power_required:                                      # Compare power possible & power required, so that not to much energy is wrongly consumed
        power_possible = power_required

      


      ChargingStation.availableL1[p_space] -= num_tickets                       # Occupy the parking lot

      "Check charging willingness"
      if parking_time < 350 | charge_preference < 20 | power_required < 5:                                                    # Check park duration of the EV
        yield env.timeout(parking_time)                                         # EV parks for x minutes
        print('%s parked in Level 1 for %.1f seconds, but did not charged due too low parking time' % (name, env.now - start))
        ChargingStation.availableL1[p_space] += num_tickets                     # Parking lot becomes available again
        
        # Track the requiered energy for the EV at home
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return

    
        
  

      "The actual charging process"  
        
      if pv_generator.level < power_possible:                                 # Check PV energy availability for the upcoming charging process
        
        yield power_grid.put(power_possible - pv_generator.level)             # Track power grid energy consumption
        item = (env.now, power_possible-pv_generator.level) 
        export_data1.append(item)
        if not pv_generator.level == 0:                                       # Check PV energy level                 
          item1 = (env.now, pv_generator.level) 
          export_data2.append(item1)
          yield pv_generator.get(pv_generator.level)                          # Track PV energy consumption / empty the pv system 
      else:
        item1 = (env.now, power_possible) 
        export_data2.append(item1)
        yield pv_generator.get(power_possible)                                # Track PV energy consumption / get the energy requiered 
        

      yield env.timeout(parking_time)                                         # EV parks for x minutes
      


      print('%s finished charging Level 1 in %.1f seconds.' % (name, env.now - start))
      ChargingStation.availableL1[p_space] += num_tickets                     # Parking lot becomes available again

      # Track the requiered energy for the EV at home
      if not power_required == power_possible:
        home_charg.put(random.randint(power_required - power_possible + 5))
        item = (env.now, random.randint(power_required - power_possible + 5)) 
        export_data.append(item)
      else:
        home_charg.put(5)
        item = (env.now, 5) 
        export_data.append(item)
        
      return

"A EV charges at a Level 2 Charging Station"
def charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1, export_data2, chargerAuslastung):

      # Set Up of the EV and the Charger
      start = env.now
      battery_capacity = random.randint(*BATTERY_SIZE)
      battery_level = random.randint(5,battery_capacity-1)
      parking_time = random.randint(*TIME_OF_STAY)
      charge_preference = random.randint(*CHARGING_PROBABILITY)
      power_required = battery_capacity - battery_level               
      power_possible = CS_SPEED_2 * parking_time
      if power_possible > power_required:                                     # Compare power possible & power required, so that not to much energy is wrongly consumed
        power_possible = power_required
        
      ChargingStation.availableL2[p_space] -= num_tickets                     # Occupy the parking lot


      "Check charging willingness"
      if parking_time < 350 | charge_preference < 20 | power_required < 5:                                                  # Check park duration of the EV
        yield env.timeout(parking_time)                                       # EV parks for x minutes
        print('%s parked in Level 2 for %.1f seconds, but did not charged due too low parking time' % (name, env.now - start))
        ChargingStation.availableL2[p_space] += num_tickets                   # Parking lot becomes available again

        # Track the requiered energy for the EV at home
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return

      



      "The actual charging process"  
        
      if pv_generator.level < power_possible:                                  # Check PV energy availability for the upcoming charging process
        
        yield power_grid.put(power_possible - pv_generator.level)              # Track power grid energy consumption
        item = (env.now, power_possible-pv_generator.level) 
        export_data1.append(item)
        if not pv_generator.level == 0:                                        # Check PV energy level
          item1 = (env.now, pv_generator.level)                                
          export_data2.append(item1)
          yield pv_generator.get(pv_generator.level)                           # Track PV energy consumption / empty the pv system 
      else:
        item1 = (env.now, power_possible) 
        export_data2.append(item1)
        yield pv_generator.get(power_possible)                                 # Track PV energy consumption / get the energy requiered
      itemx = (parking_time) 
      chargerAuslastung.append(itemx)
      yield env.timeout(parking_time)                                          # EV parks for x minutes  

      
      print('%s finished charging Level 2 in %.1f seconds.' % (name, env.now - start))
      ChargingStation.availableL2[p_space] += num_tickets                      # Parking lot becomes available again

      # Track the requiered energy for the EV at home
      if not power_required == power_possible:
        home_charg.put(random.randint(power_required - power_possible + 5))
        item = (env.now, random.randint(power_required - power_possible + 5)) 
        export_data.append(item)
      else:
        home_charg.put(5)
        item = (env.now, 5) 
        export_data.append(item)

      return

"A Vehicle parks at a regular parking spot"
def parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data):
   
        
  if car_type ==  2:                                                       # Check if an EV parks at the regular parking spot
    # Set Up the properties of the EV for the Home Charging consumption
    battery_capacity = random.randint(*BATTERY_SIZE)
    battery_level = random.randint(5,battery_capacity-1)
    power_required = battery_capacity - battery_level

    # Track the requiered energy for the EV at home
    home_charg.put(power_required + random.randint(5,battery_level))
    item = (env.now, power_required + random.randint(5,battery_level)) 
    export_data.append(item)

  parking_time = random.randint(*TIME_OF_STAY)                             # Set the parking duration
  ChargingStation.available[p_space] -= num_tickets                        # Occupy the parking lot
  yield env.timeout(parking_time)                                          # Vehicle / EV parks for x minutes                                       
  print(name + ' Parks for %.1f' % (env.now))
  ChargingStation.available[p_space] += num_tickets                        # Parking lot becomes available again
  return

"The Production of Energy from the PV systems"
def pv_producer(env, pv_generator):
    
    
    while True:                                                           # PV produce every hour a certain amount of energy
      
      
      if env.now >= 32400 and env.now <= 57600:                           # from 9 am - 4 pm       
        if env.now >= 39600 and env.now <= 52200:                         # from 11 am - 2:30 pm
          pv_generator.put((PV_GENERATION + 0.1) * PV_COUNT)              # Produce more energy and store it

        else:
          pv_generator.put((PV_GENERATION - 0.1) * PV_COUNT)              # Produce less energy and store it


      print(pv_generator.level)
      yield env.timeout(3600)                                             # Update every hour 
      
"A Vehicle / EV is generated for the Simulation"
def car_generator(env, parking_loot, charge_station, export_data, export_data1, export_data2, chargerAuslastung):
    "Generate new cars that arrive at the parking loot."
    
    for i in itertools.count():                                             # Generate cars depending on the time of Day
        
        if env.now <= 3600:                                                 # 3 600 Seconds = 1 Hour
            yield env.timeout(random.randint(40,50))
        elif env.now <= 7200:
            yield env.timeout(random.randint(70,80))
        elif env.now <= 10800:
            yield env.timeout(random.randint(75,85))
        elif env.now <= 14400:
            yield env.timeout(random.randint(90,100))
        elif env.now <= 18000:
            yield env.timeout(random.randint(100,110))
        elif env.now <= 21600:
            yield env.timeout(random.randint(100,110))
        elif env.now <= 25200:
            yield env.timeout(random.randint(95,105))
        elif env.now <= 28800:
            yield env.timeout(random.randint(40,50))
        elif env.now <= 32400:
            yield env.timeout(random.randint(60,70))
        elif env.now <= 36000:
            yield env.timeout(random.randint(40,50))
        elif env.now <= 39600:
            yield env.timeout(random.randint(35,45))
        elif env.now <= 43200:
            yield env.timeout(random.randint(35,45))
        elif env.now <= 46800:
            yield env.timeout(random.randint(35,45))
        elif env.now <= 50400:
            yield env.timeout(random.randint(30,40))
        elif env.now <= 54000:
            yield env.timeout(random.randint(30,40))
        elif env.now <= 57600:
            yield env.timeout(random.randint(30,40))
        elif env.now <= 61200:
            yield env.timeout(random.randint(30,40))
        elif env.now <= 64800:
            yield env.timeout(random.randint(25,35))
        elif env.now <= 68400:
            yield env.timeout(random.randint(45,55))
        elif env.now <= 72000:
            yield env.timeout(random.randint(40,50))
        elif env.now <= 75600:
            yield env.timeout(random.randint(60,70))
        elif env.now <= 79200:
            yield env.timeout(random.randint(60,70))
        elif env.now <= 82800:
            yield env.timeout(random.randint(60,70))
        elif env.now <= 86400:
            yield env.timeout(random.randint(40,50))
        
            
        
        #create a EV or a regualr vehicle
        car_type = random.randint(0,100)
        if car_type <=  EV_ADOPTION:                                         # Craete EV depending on the EV Adoption 
          car_type = 2                                                       # EV
        else:
          car_type =1                                                        # regular vehicle 



        if car_type ==  2:                                                  # Set Up charging station Level prefference 
          p_space = 'Level 2'
          
        else:
          p_space = 'normal'
        
        
        num_tickets = 1                                                     # Set Up car size 1 = 1 parking space / For future Work with Trailer or truck
        print(p_space, car_type)
        
        env.process(arrival('Car %d' % i, env, parking_loot, car_type, p_space, num_tickets, charge_station, export_data, export_data1, export_data2, chargerAuslastung)) # Arrival process is triggered 
                                                                            

"Set Up of the Simulation Environment"        
i = 35
j = 1
while i <36:
  a = []
  NORMAL_SPACES -= i
  CS_COUNT_2 = i
  while j < 101:      #101
 
   
   #Create ParkingFacility as a collecter
   ParkingFacility = collections.namedtuple('ChargingStation', 'parking_loot, parking_space, available, availableL1, availableL2 ''sold_out')


   # Setup and start the simulation
   print('Parking Loot with Chargingstations')
   env = simpy.Environment()

   
   




   # Create ParkingFacility 
   parking_loot = simpy.Resource(env,  35)
   parking_space = ['normal','Level 1', 'Level 2']
   available = {p_space: NORMAL_SPACES for p_space in parking_space}
   availableL1 = {p_space: CS_COUNT_1 for p_space in parking_space}
   availableL2= {p_space: CS_COUNT_2 for p_space in parking_space}
   sold_out = {p_space: env.event() for p_space in parking_space}

   ParkingFacility = ParkingFacility(parking_loot, parking_space, available, availableL1, availableL2, sold_out)

   pv_generator = simpy.Container(env, PV_STORE, init=0)
   power_grid = simpy.Container(env, 100000, init=0)
   home_charg = simpy.Container(env, 100000, init=0)

   export_data = []           #Home Charge Energy
   export_data1 = []          #Energy Consumption over the Day
   export_data2 = []          #PV Energy Used

   chargerAuslastung = []

   # Create environment and start processes
   env.process(pv_producer(env, pv_generator))
   env.process(car_generator(env, parking_loot, ParkingFacility, export_data, export_data1, export_data2, chargerAuslastung))

   # Execute!
   env.run(until=SIM_TIME)


   #Analyze
   sumCharge = sum(chargerAuslastung)
 
   prozentValue = round(((sumCharge / CS_COUNT_2) / 86400) * 100)

   itemx = (j, round(power_grid.level), prozentValue) 
   a.append(itemx)
 
 
   print( a )
   print (' %d was gatherd from the power grid' % (power_grid.level))
   print (' %d was gatherd from the power grid at home' % (home_charg.level))

 
   # Convert track data
   my_df = pd.DataFrame(export_data)
   my_df1 = pd.DataFrame(export_data1)
   my_df2 = pd.DataFrame(export_data2)
   my_df3 = pd.DataFrame(a)

 

   #Export data
   #my_df.to_csv('%i homechargewithevandPV +%i.csv' % (j,i), index=False, header=True)
   my_df1.to_csv('%i chargeenergywithPV +%i.csv' % (i,j), index=False, header=True)
 
   # my_df2.to_csv('PVEnergyConsumption +%i.csv' % (i), index=False, header=True)
   j  += 1

  #my_df3.to_csv('%i Opt +%i.csv' % (i,j), index=False, header=True)
  i  += 1
  j = 1



