import pandas as pd
import warnings 
from datetime import datetime

pd.set_option('display.max_rows',200)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',190)
pd.set_option('display.max_colwidth',50)
pd.set_option('display.expand_frame_repr',True)


warnings.simplefilter('ignore')

import os
df = pd.DataFrame()
for filename in os.listdir(os.getcwd()+'\\experiment_results'):
   df_new = pd.read_pickle(os.getcwd()+ '\\experiment_results\\' +filename)

   df = pd.concat([df,df_new])
   
print(df)
df.to_pickle('test.plk')

grouped_df = df.groupby('threshold').mean()
