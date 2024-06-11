import twstock
import os
from datetime import datetime
import glob
import mplfinance as mpf
import pandas as pd
import numpy as np
import time
import tabula
 
today=datetime.today().date()
all_stocks = twstock.codes

#creat folder at D://stock and name as the date of "today"
def create_folder(folder_path):
    save_folder = os.path.join(os.path.dirname(folder_path),'data_fig')
    save_folder_f = os.path.join(os.path.dirname(folder_path),'data_files')
    folder_paths=[folder_path, save_folder,save_folder_f,os.path.join(save_folder,'rise'),
                  os.path.join(save_folder,'fall'),os.path.join(save_folder_f,'rise'),
                  os.path.join(save_folder_f,'fall')]
    for folder in folder_paths:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                print('Create folder ERROR.')
        else:
            print(f"The {folder} already exsists.")
    return folder_path,save_folder,save_folder_f

#List filename of image file in the "folder_path"
def check_data(folder_path):
    excel_files=[]
    excel_files += [os.path.basename(file)[:-4] for file in glob.glob(os.path.join(folder_path, '*.csv'))]
    excel_files += [os.path.basename(file)[:-5] for file in glob.glob(os.path.join(folder_path, '*.xlsx'))]
    excel_files += [os.path.basename(file)[:-4] for file in glob.glob(os.path.join(folder_path, '*.txt'))]
    return excel_files

#Collect the data of stock from the year, month and save in the folder_path
def catch_the_data_of_twstock(rawdata_folder,year,month,code):
    start_time=time.time()
    if code in all_stocks:
        stock=twstock.Stock(code)
        stock_data= stock.fetch_from(year,month)
        df = pd.DataFrame(stock_data)
        if not df.empty:
            file_name=f'{rawdata_folder}/{code}.txt'
            end_time=time.time()
            print(code,'time',end_time-start_time)
            return df,file_name
        else:
            return None,None
    else:
        return None,None

#counter
def counter_ic(file,savefig_folder,savefiles_folder):
    if not os.path.exists(f'{savefig_folder}/rise/{file}'):
        os.makedirs(f'{savefig_folder}/rise/{file}')
    if not os.path.exists(f'{savefig_folder}/fall/{file}'):
        os.makedirs(f'{savefig_folder}/fall/{file}')
    if os.path.exists(f'{savefiles_folder}/rise/{file}'):
        counter=len(check_data(f'{savefiles_folder}/rise/{file}'))
    else:
        os.makedirs(f'{savefiles_folder}/rise/{file}')
        counter=0
    if os.path.exists(f'{savefiles_folder}/fall/{file}'):
        counter+=len(check_data(f'{savefiles_folder}/fall/{file}'))
    else:
        os.makedirs(f'{savefiles_folder}/fall/{file}')
        counter+=0
    return counter

#Collect the num and code name from the folder_path
def Database(rawdata_folder,savefig_folder,savefiles_folder):
    files=check_data(rawdata_folder)
    if not os.path.exists(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt')):
        database={'code_num':files}
        dbf=pd.DataFrame(database)
        quantity=[]
        latest_date=[]
        counters=[]
        for file in files:
            data=pd.read_csv(f'{rawdata_folder}/{file}.txt', sep="\t", header=0)
            df=pd.DataFrame(data)
            row=df.shape[0]
            quantity.append(row)
            counters.append(counter_ic(file,savefig_folder,savefiles_folder))
            latest_date.append(df['date'].iloc[-1])
        dbf['quantity']=quantity
        dbf['latest_date']=latest_date
        dbf['counter']=counters
    else:
        database=pd.read_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'))
        dbf=pd.DataFrame(database)
        for file in files:
            data=pd.read_csv(os.path.join(rawdata_folder,f'{file}.txt'), sep="\t", header=0)
            df = pd.DataFrame(data)
            quantity=df.shape[0]
            latest_date=df['date'].iloc[-1]
            counter=counter_ic(file,savefig_folder,savefiles_folder)
            if not file in list(dbf['code_num']):
                new_row={'code_num': file, 'quantity': quantity,'latest_date':latest_date,'counter':counter}
                dbf = pd.concat([dbf, pd.DataFrame([new_row])])
            else:
                index = dbf[dbf['code_num'] == file].index
                dbf.at[index[0], 'counter']=counter
                if dbf.iloc[index[0]]['quantity'] != quantity:
                    dbf.at[index[0], 'quantity'] = quantity
                    dbf.at[index[0], 'latest_date'] = latest_date
    dbf.to_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'), index=False)
    return dbf

#collecting the training fig and file from the raw_data 
def collecting(rawdata_folder,savefig_folder,savefiles_folder):
    start_time=time.time()
    condition=['fall','rise']
    dbf=Database(rawdata_folder,savefig_folder,savefiles_folder)
    files=dbf['code_num']

    for file in files:
        index_file = dbf[dbf['code_num'] == file].index
        counter = dbf.iloc[index_file[0]]['counter']
        quantity=int(dbf.iloc[index_file[0]]['quantity'])
        if quantity-counter>50:
            data=pd.read_csv(os.path.join(rawdata_folder,f'{file}.txt'), sep="\t", header=0)
            df = pd.DataFrame(data)
            df['date']=pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            for n in range(quantity-counter-50):
                source=df.iloc[counter+n:counter+39+n]
                purchase_price=df.iloc[counter+39+n]['high']/2+df.iloc[counter+39+n]['low']/2
                selling=df.iloc[counter+n+45:counter+n+49]
                selling_price=selling['high'].mean()/2+selling['low'].mean()/2
                if (selling_price/purchase_price)-1 > 0.04:
                    index=1
                else:
                    index=0
                mc = mpf.make_marketcolors(up='r',
                        down='g',
                        edge='',
                        wick='inherit',
                        volume='inherit')
                s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
                mpf.plot(source, type='candle', volume=False, title=file, style=s, savefig=f'{savefig_folder}/{condition[index]}/{file}/{file}_{counter+n}')
                df.to_csv(f'{savefiles_folder}/{condition[index]}/{file}/{file}_{counter+n}.txt', sep='\t', index=False)
                dbf.at[index_file[0],'counter'] = counter+n
                dbf.to_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'), index=False)
    end_time=time.time()
    during_time=end_time-start_time
    print(during_time)
    return dbf

#Catch the stock num from pdf
def update_data_from_pdf(pdf_path,rawdata_folder,savefig_folder,savefiles_folder):
    if os.path.exists(pdf_path):
        tables = tabula.read_pdf(pdf_path, pages="all")
        table_data = []
        for table in tables:
            table_data.append(table.values.tolist())
        table_data=np.vstack(table_data)
        target_stock = []
        for row in table_data:
            for cell in row:
                if isinstance(cell, (int)):
                    if cell>1000:
                        target_stock.append(str(cell))
                    else:
                        target_stock.append('00'+str(cell))
                elif isinstance(cell, str):
                    try:
                        number = float(cell)
                        if number>1000:
                            target_stock.append(cell)
                        else:
                            target_stock.append('00'+cell)
                    except ValueError:
                        pass
        files=check_data(rawdata_folder)
        for code in target_stock:
            if not code in files:
                df,file_name=catch_the_data_of_twstock(rawdata_folder,2014,1,code)
                if not df.empty:
                    df.to_csv(file_name,index=False,sep='\t')
        dbf=Database(rawdata_folder,savefig_folder,savefiles_folder) #save the database in the file
        print("completed")
        return dbf
    else:
        print('The file does not exist')
        return None

#Update the stock-data to today
def update_raw_data(rawdata_folder,savefig_folder,savefiles_folder,start_code):
    database=pd.read_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'))
    dbf=pd.DataFrame(database)
    target_stock=dbf['code_num']
    index=dbf[dbf['code_num']==start_code].index
    today = datetime.today()
    for i in range(len(target_stock)-index[0]):
        code=dbf['code_num'].iloc[i+index[0]]
        data=pd.read_csv(f'{rawdata_folder}\{code}.txt',sep='\t',header=0)
        df=pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        last_date=df['date'].iloc[-1]
        days_diff = (today.date() - last_date.date()).days
        if days_diff>0:
            month=last_date.month
            year=last_date.year
            dfu,file_name=catch_the_data_of_twstock(rawdata_folder,year,month,code)
            if not dfu is None:
                matching_index = dfu[dfu['date'] == last_date.strftime('%Y-%m-%d')].index
                dfu = dfu.drop(dfu.index[0:matching_index[0]+1])
                df=pd.concat([df,dfu])
                df.to_csv(file_name,index=False,sep='\t')
        else:
            print('finished or check the folder')
    dbf=Database(rawdata_folder,savefig_folder,savefiles_folder) #save the database in the file
    return dbf

#-------main code---------- 
folder_path='D:/stock/raw_data'
rawdata_folder,savefig_folder,savefiles_folder=create_folder(folder_path)
collecting(rawdata_folder,savefig_folder,savefiles_folder)
