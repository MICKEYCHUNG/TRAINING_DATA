import pandas as pd
import twstock
import mplfinance as mpf
import numpy as np
import os
from datetime import datetime,timedelta
import glob

# Define:The (num) month period prior to today as the starting date for data extraction
def start_date(num):
    if datetime.today().month>num:
        year=datetime.today().year
        month=datetime.today().month-num
    else:
        year=datetime.today().year-1
        month=12-num+datetime.today().month
    return year,month
#return year,month

# Define:Create a folder to save the fig of target_stock and name as date of today
def create_folder():
    Today=datetime.today().date()
    folder_path=f'D:/stock/fig/{Today}_human'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return(folder_path)
#return folder_path

# Define:Get fignames without '.png' and '.jpg' extensions in the folder
def check_fig(folder_path):
    image_files = glob.glob(os.path.join(folder_path,'*'))
    valid_filenames = [os.path.splitext(os.path.basename(file))[0] for file in image_files]
    return valid_filenames
#return valid_filenames

# Save the whole stock_data, I conerned about, as a fig in the folder.
def catch_stock_num(stock_num,valid_filenames,folder_path,year,month):
    # Read each stock in stock_num
    for i in range(len(stock_num)):
        # check the stock still exsistence or not
        if stock_num[i] in all_stock and not stock_num[i] in valid_filenames:
            stock = twstock.Stock(stock_num[i]) #get the information of each stock
            target_price=stock.fetch_from(year,month)
            name_attribute = [
                'Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change','Transcation'
            ] # setting the title of each data of stock
            df=pd.DataFrame(columns=name_attribute,data=target_price)
            # check the data empty or not
            if not df.empty:
                print(stock_num[i])
                df['Date']=pd.to_datetime(df['Date'])
                df.set_index('Date',inplace=True)
                # Plot the fig of target_stock and save it
                mc = mpf.make_marketcolors(up='r',
                        down='g',
                        edge='',
                        wick='inherit',
                        volume='inherit') # define the type of candle plot
                s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
                mpf.plot(df, type='candle', style=s,title=f'{stock_num[i]}',
                        volume=False, savefig=f'{folder_path}/{stock_num[i]}.png')
                # Draing fig and save it to the target folder

#Catch one stock data as fig
def catch_one_stock(code_name):
    # check the stock still exsistence or not
    if code_name in all_stock:
        stock = twstock.Stock(code_name) #get the information of each stock
        target_price=stock.fetch_from(year,month)
        name_attribute = [
            'Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change','Transcation'
        ] # setting the title of each data of stock
        df=pd.DataFrame(columns=name_attribute,data=target_price)
        # check the data empty or not
        if not df.empty:
            df['Date']=pd.to_datetime(df['Date'])
            df.set_index('Date',inplace=True)
            # Plot the fig of target_stock and save it
            mc = mpf.make_marketcolors(up='r',
                    down='g',
                    edge='',
                    wick='inherit',
                    volume='inherit') # define the type of candle plot
            s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
            mpf.plot(df, type='candle', style=s,title=f'{code_name}', volume=False)
            # Draing fig

all_stock=twstock.codes.keys() #ALL stock num in TW

## --------------------------  main code -------------------------------------------##

#The array stock num I conerned.
folder_path='D:\stock\data'
stock_num=check_fig(folder_path)
quantity=0
num=3
year,month=start_date(num)
folder_path=create_folder()
valid_filenames=check_fig(folder_path)
catch_stock_num(stock_num,valid_filenames,folder_path,year,month)