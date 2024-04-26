from prog_models.models import CentrifugalPump
import numpy as np
import random

class Pump():
        
    def __init__(self):
        self.pump = CentrifugalPump(process_noise= 0.000000000001)
        self.pump.parameters['x0']['wA'] = 0.01  # Set Wear Rate
        self.states = self.pump.parameters['x0']
        self.initial_params = self.pump.parameters
        self.V = 471.2389
        self.cycletime= 3600
        self.options = {
                        'save_freq': 100, # Frequency at which results are saved
                        'dt': 2 # Timestep
                        } 
        self.temp = 290
    
    def set_seed(self, s=42):
        np.random.seed(s)
        random.seed(s)
        
    def future_loading(self,t, x=None): 
        return self.pump.InputContainer({
            'Tamb': self.temp,
            'V': self.V,
            'pdisch': 928654, 
            'psuc': 239179, 
            'wsync': self.V * 0.8
        })
    
    def get_health(self, action):
        self.V = action
        self.pump.parameters['x0'] = self.states
        (_, _, states, outputs, event_states) = self.pump.simulate_to(100, self.future_loading, **self.options)
        self.states = states[-1]
        health = event_states[-1]
        health = self.get_min_health(health)
        return health
    
    def repair(self):
        self.pump.parameters =  self.initial_params

    
    def get_min_health(self, health):
        h = 1
        for k in health.keys():
            if health[k]<h:
                h = health[k]
        return h
    
    def set_temp(self, celsius_wert):
        result = float(celsius_wert) + 273.15
        self.temp = result    

    
if __name__ == "__main__":
    
    p = Pump()
    # p.set_seed(2022)
    h = 1
    i = 0
    p.set_temp(50)
    # p.repair()
    while h>0:
        
        h = p.get_health(471.2389)
        print(f"{h}")
    h = p.get_health(471.2389)  
    print(f"{h}")

# pump = CentrifugalPump(process_noise= 0)
# pump.parameters['x0']['wA'] = 0.01  # Set Wear Rate
# cycle_time = 3600
# V=400
# def future_loading(t, x=None):
#         return pump.InputContainer({
#             'Tamb': 290,
#             'V': V,
#             'pdisch': 928654, 
#             'psuc': 239179, 
#             'wsync': V * 0.8
#         })
    
# options = {
#     'save_freq': 100, # Frequency at which results are saved
#     'dt': 2 # Timestep
#     }   

# (_, _, states, outputs, event_states) = pump.simulate_to(100, future_loading, **options)
# health = event_states[-1]['EOD'] 
    
    
# def produce_model(machine, states, action): # TODO: Allow seed

#   # Define load of battery

#   def future_loading(t, x=None):
#   return {'i': action}


#   # Set current state of machine
#   machine.parameters['x0'] = states

 

#   # Simulate 100 steps

#   options = {

#   'save_freq': 100, # Frequency at which results are saved

#   'dt': 2 # Timestep

#   }

#   (_, _, states, outputs, event_states) = machine.simulate_to(100, future_loading, **options)

#   health = event_states[-1]['EOD']

#   return(round(health, 2), states[-1], outputs[-1]['t'],
# outputs[-1]['v'])
