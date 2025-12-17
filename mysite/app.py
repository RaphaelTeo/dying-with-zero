
from flask import Flask, request, render_template
import pandas as pd
pd.set_option('display.float_format', '{:.0f}'.format)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io
import base64

app = Flask(__name__)

def create_df(age,retirement_age,final_age,age_lst,expenses_lst,income,init,returns, special_dict):
    income_lst = [income] * (retirement_age-age-1)
    zeroincome = [0] * (final_age-retirement_age)
    income_lst.insert(0,0)
    income_lst.extend(zeroincome)

    df = pd.DataFrame(columns=['Age','Yearly Income $ (\'000)','Yearly Expenses $ (\'000)','Cumulative Cash $ (\'000)'])
    df['Age']=age_lst
    df['Yearly Expenses $ (\'000)']=expenses_lst
    df['Yearly Income $ (\'000)']=income_lst
    cum_calc = []
    for i in range(len(df)): # populate 'cumulative' list
        if i == 0:
            cum = init
        else:
            cum = (cum_calc[i-1]*returns) + df.loc[i,'Yearly Income $ (\'000)'] - df.loc[i, 'Yearly Expenses $ (\'000)']

        if (age+i) in special_dict: # for special adds
            cum += special_dict[age+i]

        cum_calc.append(cum)
        
    df['Cumulative Cash $ (\'000)'] = cum_calc # add to df
    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    final_age = 121
    number_of_charts = 5
    error = None
    image_data = None
    summary = None
    table = None
    tableheader = None
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            retage = int(request.form['retage'])
            returns_perc = round(float(request.form['returns']),2)
            returns = round((returns_perc/100)+1,5)
            income = (float(request.form['income'])/1000)
            expenses = (float(request.form['expenses'])/1000)
            init = (float(request.form['init'])/1000)
            if (not request.form['specialages']) and (not request.form['specialadds']): # both empty
                special_dict = {} # empty dict, continue

            elif (request.form['specialages']) and (request.form['specialadds']): # both filled
                specialages = [int(item) for item in str(request.form['specialages']).split(",")]
                specialadds = [float(item)/1000 for item in str(request.form['specialadds']).split(",")]
                special_dict = dict(zip(specialages,specialadds))

            else:
                error = 'Input error, please follow the extraordinary cash flow example.'
                return render_template("index.html", error=error, image_data=image_data, summary=summary, table=table, tableheader=tableheader) #exit workflow
            '''
            try: # nested try for optional special values
                specialages = [int(item) for item in str(request.form['specialages']).split(",")]
                specialadds = [float(item)/1000 for item in str(request.form['specialadds']).split(",")]
                special_dict = dict(zip(specialages,specialadds))
            except:
                if (not request.form['specialages']) and (not request.form['specialadds']) or (request.form['specialages']) and (request.form['specialadds']): # both are empty or both are filled
                    special_dict = {} # empty dict, continue
                else:
                    error = 'Input error, please follow the example.'
                    return render_template("index.html", error=error, image_data=image_data, summary=summary, table=table, tableheader=tableheader) #exit workflow
'''
            step = round((retage-age)/number_of_charts) # returns int by default if not specified
            retirement_age_list = list(range(age+1,retage+1,step))
            if retage not in retirement_age_list: # sometimes the step value skips the actual retage
                retirement_age_list.append(retage)
            age_lst = [i for i in  range(age,final_age)]
            expenses_lst = [expenses] * (final_age-age-1)
            expenses_lst.insert(0,0)
            
            for retirement_age in retirement_age_list:
                df = create_df(age,retirement_age,final_age,age_lst,expenses_lst,income,init,returns, special_dict)
                plt.plot(df['Age'],df['Cumulative Cash $ (\'000)'],label=retirement_age)
                #print(df)
                #df.to_csv(f'my_data {retirement_age}.csv')

            table = df.to_html(index=False) # only display the last df of the selected retirement age

            plt.grid(True, which='both', linestyle='--', linewidth=0.5)

            plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
            plt.xlabel('Age')
            plt.xticks(rotation=45)
            plt.ylabel('Cumulative $ (\'000)')
            plt.title(f'DWZ plan for different retirement ages')
            plt.tight_layout()
            plt.legend(bbox_to_anchor=(0, 1), loc='upper left')
            plt.ylim(bottom=-200,top=2000)
            ax = plt.gca() # get current axis
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
            #plt.savefig(f'Sustainability {init_cumulative}k inc {yearly_income}k exp {yearly_expense}k at {round((returnedcapital-1),2)*100} percent.png', dpi=300)
            #plt.show()

            # Output plot directly to BytesIO
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

            summary = f'DWZ plan with {init}k + income {income}k + expenses {expenses}k at {returns_perc}% return. Extraordinary cashflows (<age>:<cashflow in thousands>): {special_dict}'
            tableheader = f'Data table for retirement at age {retage} ($ \'000)'

        except Exception as e:
            #print (e)
            error = f"error: {e}"

    return render_template("index.html", error=error, image_data=image_data, summary=summary, table=table, tableheader=tableheader) 

if __name__ == '__main__':
    app.run(debug=True)