from prog_models.models import CentrifugalPump
import pandas as pd
import numpy as np
import random
import pickle
import warnings 
from datetime import datetime


warnings.simplefilter('ignore')

class Pump():

    def __init__(self):
        self.pump = CentrifugalPump(process_noise= 0.000000000001)
        self.pump.parameters['x0']['wA'] = 0.009  # Set Wear Rate
        self.states = self.pump.parameters['x0']
        self.initial_params = self.pump.parameters
        self.V = 471.2389
        self.cycletime= 3600
        self.options = {
                        'save_freq': 100, # Frequency at which results are saved
                        'dt': 2 # Timestep
                        }
        self.temp = 290
        self.product_types = {1: {'temp': 50, 'V': 230},
                              2: {'temp': 45, 'V': 230},
                              3: {'temp': 40, 'V': 230},
                              4: {'temp': 38, 'V': 230},
                              5: {'temp': 33, 'V': 230},
                              6: {'temp': 30, 'V': 230},}

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
    
    def get_health_pypline(self, prod_type):
        action = self.product_types[prod_type]
        action['duration'] = 180
        health = self.get_health(action)
        return self.get_min_health(health)
    
    def get_health(self, action):
        self.V = action['V']
        self.set_temp(action['temp'])
        self.pump.parameters['x0'] = self.states
        (_, _, states, outputs, event_states) = self.pump.simulate_to(action['duration'], self.future_loading, **self.options)
        self.states = states[-1]
        health = event_states[-1]
        # health = self.get_min_health(health)
        return health

    def repair(self):
        # self.pump.parameters =  self.initial_params
        self.pump = CentrifugalPump(process_noise= 0.000000000001)
        self.pump.parameters['x0']['wA'] = 0.009  # Set Wear Rate
        self.states = self.pump.parameters['x0']


    def get_min_health(self, health):
        h = 1
        for k in health.keys():
            if health[k]<h:
                h = health[k]
        return h

    def set_temp(self, celsius_wert):
        result = float(celsius_wert) + 273.15
        self.temp = result
        
    def get_current_health(self):
        return self.get_min_health(self.pump.event_state(self.states))
        
    def get_prediction_info(self, as_dict=True):
        state = self.states
        # print('state')
        # print(state)
        event_state = self.pump.event_state(self.states)
        # print('event_state')
        # print(event_state)
        state.update(event_state)

        try:
            # print('try')
            # print(state)
            # del state['QLeak']
            state['QLeak']  = -8.303463132934355e-08
        except:
            # print('except')
            # print(state)
            state['QLeak']  = -8.303463132934355e-08
        # print('pred_info')   
        pred_info = state

        # pred_info = pd.DataFrame(state)
        
        return pred_info
        
    def schreib(self):
        print('repair')
        
    def schreib2(self):
        print('broken')

class Prescriptive_decision_maker():
    
    def __init__(self,threshold=0.99):
        self.rf = pickle.load(open("rf_pump_classifier.sav", 'rb'))
        self.threshold = threshold
        self.product_types = {1: {'temp': 50, 'V': 230},
                              2: {'temp': 45, 'V': 230},
                              3: {'temp': 40, 'V': 230},
                              4: {'temp': 38, 'V': 230},
                              5: {'temp': 33, 'V': 230},
                              6: {'temp': 30, 'V': 230},}
        
    def make_maintenance_action(self,prod_type, amount, pump, with_thresh=False):
        
        
        pred_info = pump.get_prediction_info(as_dict=True)
        # print(pred_info)
        action = self.product_types[prod_type]
        action['duration'] = amount*180
        pred_info.update(action)
        # print(pred_info)
        
        X_cols = ['w', 'Q', 'Tt', 'Tr', 'To', 'A', 'rRadial', 'rThrust', 'wA', 'wRadial', 'wThrust', 'ImpellerWearFailure', 'ThrustBearingOverheat', 'RadialBearingOverheat', 'QLeak','PumpOilOverheat', 'temp', 'V', 'duration']
        X = self.make_df(pred_info)[X_cols]
        
        # X = np.array(list(pred_info.values())).reshape(1,19)

        if with_thresh:
            y_pred = self.rf.predict_proba(X)[0][0]
            # print(y_pred)
            return y_pred
            # if y_pred<self.threshold:
            #     return 1
            # else: 
            #     return 0
        else:
            y = float(self.rf.predict(X)[0])
            # print(y)
            return y
        
    def make_df(self, pred_info):
        px = dict()
        # keys = list(pred_info.keys())
        for k in list(pred_info.keys()):
            px[k] = [pred_info[k]]
 
        df_x = pd.DataFrame(px)
        return df_x

    def save_results(self, threshold,Ausbringungsmenge, Breakdowns, Predictives, cycle_time, Order_Flow_Time, Order_Lead_Time, Orders_abgeschlossen, Orders_eingegangen,Warenträger_eingang,  tbf, experiment='test',):
        ts = datetime.now().strftime("%H_%M_%S_%f")
        data = {'experiment':[experiment],
                'threshold':[threshold],
                'Orders_eingegangen':[Orders_eingegangen],
                'Orders_abgeschlossen':[Orders_abgeschlossen],
                'Warenträger_eingang': [Warenträger_eingang],
                'Ausbringungsmenge':[Ausbringungsmenge], 
                'Breakdowns':[Breakdowns], 
                'cycle_time':[cycle_time], 
                'Order_Flow_Time':[Order_Flow_Time], 
                'Order_Lead_Time':[Order_Lead_Time],
                'Predictives':[Predictives], 
                'tbf':[tbf]}
        
        df = pd.DataFrame(data)
        
        df.to_pickle(f'experiment_results/{experiment}_{ts}.plk')
        
    
if __name__ == "__main__":
    
    p = Pump()
#     # p.set_seed(2022)
    action = {'temp': 30, 'V': 230, 'duration':180*10}
    h = 1
    i = 0

    pdm = Prescriptive_decision_maker()
    # pdm.save_results(0.7, 7, 0, 2)
#     # p.set_temp(50)
#     # # p.repair()
    while h>0.95:
        h = p.get_health_pypline(1)
        m = pdm.make_maintenance_action(5, 7, p)
        
        print(f"{i}: {h} Maintenance: {m}")
        i += 1
        
#     p.repair()
        
#     p.get_prediction_info(as_dict=True)    
    pdm.save_results(threshold=0.7,Ausbringungsmenge=77, Breakdowns=77, Predictives=77, cycle_time=0, Order_Flow_Time=0, Order_Lead_Time=0, experiment='test',Orders_abgeschlossen=77, Orders_eingegangen=77,Warenträger_eingang=77, tbf=0) 
        

    # pdm.make_maintenance_action(1, 20, p,with_thresh=False)
    # h = p.get_health(471.2389)  
    # print(f"{h}")

