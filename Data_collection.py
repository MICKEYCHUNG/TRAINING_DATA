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

#creat folder at D://stock and name as the date of "today"
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except:
            print('Create folder ERROR.')
    else:
        print(f"The {folder_path} already exsists.")
    return folder_path

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
    stock=twstock.Stock(code)
    stock_data= stock.fetch_from(year,month)
    df = pd.DataFrame(stock_data)
    if not df.empty:
        file_name=f'{rawdata_folder}/{code}.txt'
        end_time=time.time()
        print(code,'time',end_time-start_time)
        return df,file_name
    else:
        print(code,'No data')
        return None,None

#Collect the num and code name from the folder_path
def Database(rawdata_folder,files):
    if not os.path.exists(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt')):
        database={'code_num':files}
        dbf=pd.DataFrame(database)
        quantity=[]
        for file in files:
            data=pd.read_csv(os.path.join(rawdata_folder,f'{file}.txt'), sep="\t", header=0)
            df = pd.DataFrame(data)
            row=df.shape[0]
            quantity.append(row)
        dbf['quantity']=quantity
    else:
        database=pd.read_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'))
        dbf=pd.DataFrame(database)
        for file in files:
            if not file in list(dbf['code_num']):
                data=pd.read_csv(os.path.join(rawdata_folder,f'{file}.txt'), sep="\t", header=0)
                df = pd.DataFrame(data)
                quantity=row=df.shape[0]
                new_row={'code_num': file, 'quantity': quantity}
                dbf = pd.concat([dbf, pd.DataFrame([new_row])])
    dbf.to_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'), index=False)
    return dbf

#collecting the training fig and file from the raw_data
def collecting(folder_path,dbf,files):
    start_time=time.time()
    save_folder = os.path.join(os.path.dirname(folder_path),'data_fig')
    save_folder_f = os.path.join(os.path.dirname(folder_path),'data_files')
    create_folder(save_folder)
    create_folder(os.path.join(save_folder,'rise'))
    create_folder(os.path.join(save_folder,'fall'))
    create_folder(os.path.join(save_folder_f,'rise'))
    create_folder(os.path.join(save_folder_f,'fall'))
    files_fall=os.listdir(os.path.join(save_folder,'fall'))
    files_rise=os.listdir(os.path.join(save_folder,'rise'))
    counter=[len(files_fall),len(files_rise)]
    condition=['fall','rise']

    dbf.set_index('code_num', inplace=True)
    quantity=0

    for file in files:
        quantity += dbf.loc[file,'quantity']
        if sum(counter)-quantity<0:
            data=pd.read_csv(os.path.join(folder_path,f'{file}.txt'), sep="\t", header=0)
            df = pd.DataFrame(data)
            df['date']=pd.to_datetime(df['date'])
            quantity = sum(counter)+dbf.loc[file,'quantity']-quantity
            row=df.shape[0]
            df.set_index('date', inplace=True)
            for n in range(row-50):
                if n-quantity>=0:
                    source=df.iloc[n:39+n]
                    purchase_price=df.iloc[39+n]['high']/2+df.iloc[39+n]['low']/2
                    selling=df.iloc[39+n+6:39+n+10]
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
                    mpf.plot(source, type='candle', volume=False, title=file, style=s, savefig=f'{save_folder}/{condition[index]}/{counter[index]}')
                    df.to_csv(f'{save_folder_f}/{condition[index]}/{counter[index]}.txt', sep='\t', index=False)
                    counter[index]+=1
    end_time=time.time()
    during_time=end_time-start_time
    return during_time

#Catch the stock num from pdf
def catch_table_from_pdf(pdf_path):
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
        return target_stock
    else:
        print('The file does not exist')
        return None

def update_raw_data(folder,dbf):
    target_stock=dbf['code_num']
    today = datetime.today()
    for code in target_stock:
        data=pd.read_csv(f'{folder}\{code}.txt',sep='\t',header=0)
        df=pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        last_date=df['date'].iloc[-1]
        days_diff = (today.date() - last_date.date()).days
        if days_diff>0:
            month=last_date.month
            year=last_date.year
            dfu,file_name=catch_the_data_of_twstock(folder,year,month,code)
            if not dfu.empty:
                matching_index = dfu[dfu['date'] == last_date.strftime('%Y-%m-%d')].index
                dfu = dfu.drop(dfu.index[0:matching_index[0]+1])
                df=pd.concat([df,dfu])
                df.to_csv(file_name,index=False,sep='\t')
        else:
            print('finished or check the folder')


#-------main code----------

pdf_path='D:/stock/stock_from_SC.pdf'
target_stock=catch_table_from_pdf(pdf_path)

rawdata_folder=create_folder('D:/stock/raw_data')
files=check_data(rawdata_folder)

year=2014
month=1
all_stock_codes=twstock.codes
#for code in target_stock:
#    if code not in files and code in all_stock_codes:
#        print(catch_the_data_of_twstock(rawdata_folder,year,month,code))

#files=check_data(rawdata_folder)
dbf=Database(rawdata_folder,files) #save the database in the file
