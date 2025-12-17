import pandas as pd
pd.set_option('display.float_format', '{:.0f}'.format)
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
#import io
#import base64

special = {31:50000, 35:-20000}

def create_df(age,retirement_age,final_age,age_lst,expenses_lst,income,init,returns):
    income_lst = [income] * (retirement_age-age-1)
    zeroincome = [0] * (final_age-retirement_age)
    income_lst.insert(0,0)
    income_lst.extend(zeroincome)

    df = pd.DataFrame(columns=['age','income','expenses','cumulative'])
    df['age']=age_lst
    df['expenses']=expenses_lst
    df['income']=income_lst
    cum_calc = []
    for i in range(len(df)):
        if i == 0:
            cum=init
        else:
            cum = (cum_calc[i-1]*returns) + df.loc[i,'income'] - df.loc[i, 'expenses']
        if i+age in special:
            cum += special[i+age]
        cum_calc.append(cum)

    df['cumulative'] = cum_calc
    return df

age = 30
retage = 40
returns_perc = 10
returns = round((returns_perc/100)+1,5)
income = 100000
expenses = 10000
init = 20000

final_age = 111
retirement_age_list = list(range(age+1,retage+1,1))
age_lst = [i for i in  range(age,final_age)]
expenses_lst = [expenses] * (final_age-age-1)
expenses_lst.insert(0,0)

for retirement_age in retirement_age_list:
    df = create_df(age,retirement_age,final_age,age_lst,expenses_lst,income,init,returns)
    #plt.plot(df['age'],df['cumulative'],label=retirement_age)

print(df)
df.to_csv('my_data.csv')