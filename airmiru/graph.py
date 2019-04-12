import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

df = pd.read_csv('PM25Log.csv', index_col=0)
df.iloc[:,4].plot()
plt.show()
