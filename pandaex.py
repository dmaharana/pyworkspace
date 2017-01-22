import pandas as pd
sports = {'Archery':'Bhutan',
         'Golf':'Scotland',
         'Sumo':'Japan',
         'Taekwondo':'South Korea'}

s = pd.Series(sports)
print s

timeit -n 100
summary = 0
for item in s:
    summary += item
