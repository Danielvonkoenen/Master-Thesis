"""
Parking lot with charging stations and PV systems



Scenario:
  A parking lot has a limited number of charging stations and PV systems. 
  The charging stations always use the generated PV energy first before accessing the power grid. 

"""
import itertools
import random
import collections
import pandas as pd

import simpy

#Scenario / Environment Properties
RANDOM_SEED = 30
T_INTER = [45, 55]           # Create a car every [min, max] seconds
SIM_TIME = 86400            # Simulation time in seconds

#Parking Spaces Properties
NORMAL_SPACES = 25           # Amount of normal parking Spaces

#PV Properties
PV_COUNT = 0                # Amount of PVs mit 1 killowatt-peak entspricht 4 bis 6 Modulen, die zusammen eine Dachfläche von 8 bis 10 Quadratmeter einnehmen.
PV_GENERATION = 0.4         # PV Generation per 1 hour  - ca. 7 Stunden Soonenlicht 1 killowatt-peak ca. 1.000 kw/h / 365 /7 = 0,4; Später Wetter abhängig
PV_STORE = 1 #PV_COUNT       # Max Energy a PV Generator can store kwh

#Charging Stations Properties
CS_COUNT_1 = 5              # Amount of Charging Stations Level 1
CS_COUNT_2 = 5              # Amount of Charging Stations Level 2
CS_SPEED_1 = 19.2          # Charging Speed - Level 2
CS_SPEED_2 = 80             # Charging Speed - Level 3 DC

#Car Properties
BATTERY_SIZE = [30, 100]    # Min von 30 kw/h - Max 100 kw/h
BATTERY_LEVEL = [5, 99]    # Min/max levels of battery level (in volt)
TIME_OF_STAY = [300,2000]       # Min/max duration of a car parking
CHARGING_PROBABILITY = [1,100]  # Percentage of an EV owner probabilty of charging his EV
EV_ADOPTION = 25                #Percentage of EV Adoption




def arrival(name, env, parking_loot, car_type, p_space, num_tickets, ChargingStation, export_data, export_data1):
    """A car arrives at the parking loot.

    If it wants to charge it  requests one of the parking loot charging stations and tries to get the
    desired amount of power from it. 

    """


  



    #charging for *time of stay*
    print('%s arriving at parking loot at %.1f' % (name, env.now))
    with parking_loot.request() as req:
        start = env.now
        
        yield req
        
        if car_type == 1:
          if(not ChargingStation.available[p_space]):
            print('kein Parkplatz frei für %s und darf nicht auf ein EV Parkplatz parken' % p_space)    #check if a praking space is free
            return
          else:
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return

          
        



        if p_space == 'Level 1':
          if not ChargingStation.availableL1[p_space]:
           print('kein Parkplatz frei für %s' % p_space)     #check if a L1 praking space is free 
          else:
            ChargingStation.availableL1[p_space] -= num_tickets
            yield req
            yield env.process(charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1))
            return

          if not ChargingStation.availableL2[p_space]:
            print('kein Parkplatz frei für Level 2')    #check if other Level is free
          else:
            ChargingStation.availableL2[p_space] -= num_tickets
            yield env.process(charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1))
            return

          if not ChargingStation.available[p_space]:
            print('kein Parkplatz frei für %s und ist sauer und fährt weg' % name)   #check if at least one is free
            battery_capacity = random.randint(*BATTERY_SIZE)
            battery_level = random.randint(5,battery_capacity-1)
            power_required = battery_capacity - battery_level
            home_charg.put(power_required + random.randint(5,battery_level))
            item = (env.now, power_required + random.randint(5,battery_level)) 
            export_data.append(item)
            return
          else:
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return
          


        if p_space == 'Level 2':
          if not ChargingStation.availableL2[p_space]:
           print('kein Parkplatz frei für %s' % p_space)     #check if a L1 praking space is free 
          else:
            ChargingStation.availableL2[p_space] -= num_tickets
            yield env.process(charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1))
            return

          if not ChargingStation.availableL1[p_space]:
            print('kein Parkplatz frei für Level 1')    #check if other Level is free
          else:
            ChargingStation.availableL1[p_space] -= num_tickets
            yield env.process(charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1))
            return

          if not ChargingStation.available[p_space]:
            print('kein Parkplatz frei für %s und ist sauer und fährt weg' % name)   #check if at least one is free
            battery_capacity = random.randint(*BATTERY_SIZE)
            battery_level = random.randint(5,battery_capacity-1)
            power_required = battery_capacity - battery_level
            home_charg.put(power_required + random.randint(5,battery_level))
            item = (env.now, power_required + random.randint(5,battery_level)) 
            export_data.append(item)
            return
          else: 
            yield env.process(parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data))
            return

        
          

        

        return


def charge_processL1(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1):

      #charge set up
      start = env.now
      battery_capacity = random.randint(*BATTERY_SIZE)
      battery_level = random.randint(5,battery_capacity-1)
      parking_time = random.randint(*TIME_OF_STAY)
      charge_preference = random.randint(*CHARGING_PROBABILITY)
      power_required = battery_capacity - battery_level               # Get the required amount of power
      power_possible = CS_SPEED_1 * parking_time
      if power_possible >= power_required:
        power_possible = power_required

      


      if parking_time < 350:
        yield env.timeout(parking_time)
        print('%s parked in Level 1 for %.1f seconds, but did not charged due too low parking time' % (name, env.now - start))
        ChargingStation.availableL1[p_space] += num_tickets
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return

      if charge_preference < 20 | power_required < 5 :
        yield env.timeout(parking_time)
        print('%s parked in Level 1 for %.1f seconds, but did not charged due too low prefference' % (name, env.now - start))
        ChargingStation.availableL1[p_space] += num_tickets
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return
        
  

      # The "actual" charging process takes some time  
        
      if pv_generator.level < power_possible:
        
        yield power_grid.put(power_possible - pv_generator.level)       #track power Grid energy consumption
        item = (env.now, power_possible-pv_generator.level) 
        export_data1.append(item)
        if not pv_generator.level == 0:
          yield pv_generator.get(pv_generator.level)
      else:
        yield pv_generator.get(power_possible)
        

      yield env.timeout(parking_time)   
      


      print('%s finished charging Level 1 in %.1f seconds.' % (name, env.now - start))
      ChargingStation.availableL1[p_space] += num_tickets 
      if not power_required == power_possible:
        home_charg.put(random.randint(power_required - power_possible + 5))
        item = (env.now, random.randint(power_required - power_possible + 5)) 
        export_data.append(item)
      else:
        home_charg.put(5)
        item = (env.now, 5) 
        export_data.append(item)
        
      return


def charge_processL2(name, env, p_space, num_tickets, ChargingStation, export_data, export_data1):

      #charge set up
      start = env.now
      battery_capacity = random.randint(*BATTERY_SIZE)
      battery_level = random.randint(5,battery_capacity-1)
      parking_time = random.randint(*TIME_OF_STAY)
      charge_preference = random.randint(*CHARGING_PROBABILITY)
      power_required = battery_capacity - battery_level               # Get the required amount of power
      power_possible = CS_SPEED_2 * parking_time
      if power_possible > power_required:
        power_possible = power_required
        
        
      if parking_time < 350:
        yield env.timeout(parking_time)
        print('%s parked in Level 2 for %.1f seconds, but did not charged due too low parking time' % (name, env.now - start))
        ChargingStation.availableL2[p_space] += num_tickets
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return

      if charge_preference < 20 | power_required < 5 :
        yield env.timeout(parking_time)
        print('%s parked in Level 2 for %.1f seconds, but did not charged due too low prefference' % (name, env.now - start))
        ChargingStation.availableL2[p_space] += num_tickets
        home_charg.put(power_required + random.randint(5,battery_level))
        item = (env.now, power_required + random.randint(5,battery_level)) 
        export_data.append(item)
        return

       # The "actual" charging process takes some time  
        
      if pv_generator.level < power_possible:
        
        yield power_grid.put(power_possible - pv_generator.level)       #track power Grid energy consumption
        item = (env.now, power_possible-pv_generator.level) 
        export_data1.append(item)
        if not pv_generator.level == 0:
          yield pv_generator.get(pv_generator.level)
      else:
        yield pv_generator.get(power_possible)
        

      yield env.timeout(parking_time)   

      
      print('%s finished charging Level 2 in %.1f seconds.' % (name, env.now - start))
      ChargingStation.availableL2[p_space] += num_tickets
      if not power_required == power_possible:
        home_charg.put(random.randint(power_required - power_possible + 5))
      else:
        home_charg.put(5)
        
      return


def parking_process(name, env, p_space, num_tickets, ChargingStation, car_type, export_data):
   #check if car is a NON EV 
        
      if car_type ==  2:
       battery_capacity = random.randint(*BATTERY_SIZE)
       battery_level = random.randint(5,battery_capacity-1)
       power_required = battery_capacity - battery_level
       home_charg.put(power_required + random.randint(5,battery_level))
       item = (env.now, power_required + random.randint(5,battery_level)) 
       export_data.append(item)

      parking_time = random.randint(*TIME_OF_STAY)
      ChargingStation.available[p_space] -= num_tickets 
      yield env.timeout(parking_time)                              #time of stay = 100
      print(name + ' Parks for %.1f' % (env.now))
      ChargingStation.available[p_space] += num_tickets 
      return


def pv_producer(env, pv_generator):
    while True:
      
      if not PV_COUNT == 0:
        pv_generator.put(PV_GENERATION * PV_COUNT)

      print(pv_generator.level)
      yield env.timeout(100)      # Update every 100 seconds
      

def car_generator(env, parking_loot, charge_station, export_data, export_data1):
    """Generate new cars that arrive at the parking loot."""
    
    for i in itertools.count():
        
        if env.now <= 3600:
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
        
            
        
        #create EV or normal 
        car_type = random.randint(0,100)
        if car_type <=  EV_ADOPTION:
          car_type = 2
        else:
          car_type =1



        if car_type ==  2:
          p_space = random.choice(['Level 1', 'Level 2'])
          #p_space = 'Level 1'       # Nur zum testen
        else:
          p_space = 'normal'
        
        
        num_tickets = 1             #Auto = 1 Parkplatz / später z.b. für LkWs etc.
        print(p_space, car_type)
        
        env.process(arrival('Car %d' % i, env, parking_loot, car_type, p_space, num_tickets, charge_station, export_data, export_data1))
        
          

i = 1
while i < 101:
 #Create Charging Stations -probably collecter
 ChargingStation = collections.namedtuple('ChargingStation', 'parking_loot, parking_space, available, availableL1, availableL2 ''sold_out')




 # Setup and start the simulation
 print('Parking Loot with Chargingstations')
 #random.seed(RANDOM_SEED)
 env = simpy.Environment()




 # Create Charging Station 
 parking_loot = simpy.Resource(env, NORMAL_SPACES + CS_COUNT_1 + CS_COUNT_2)
 parking_space = ['normal','Level 1', 'Level 2']
 available = {p_space: NORMAL_SPACES for p_space in parking_space}
 availableL1 = {p_space: CS_COUNT_1 for p_space in parking_space}
 availableL2= {p_space: CS_COUNT_2 for p_space in parking_space}




 sold_out = {p_space: env.event() for p_space in parking_space}

 ChargingStation = ChargingStation(parking_loot, parking_space, available, availableL1, availableL2, sold_out)


 pv_generator = simpy.Container(env, PV_STORE, init=0)
 power_grid = simpy.Container(env, 100000, init=0)
 home_charg = simpy.Container(env, 100000, init=0)

 export_data = []
 export_data1 = []



 # Create environment and start processes
 env.process(pv_producer(env, pv_generator))
 env.process(car_generator(env, parking_loot, ChargingStation, export_data, export_data1))

 # Execute!
 env.run(until=SIM_TIME)
 print (' %d was gatherd from the power grid' % (power_grid.level))
 print (' %d was gatherd from the power grid at home' % (home_charg.level))

 

 my_df = pd.DataFrame(export_data)
 my_df1 = pd.DataFrame(export_data1)

 my_df.to_csv('homechargewithev +%i.csv' % (i), index=False, header=True)
 my_df1.to_csv('chargeenergy +%i.csv' % (i), index=False, header=True)
 i  += 1




