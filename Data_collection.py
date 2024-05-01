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
        file_name=f'{rawdata_folder}/{code} .txt'
        df.to_csv(file_name, sep='\t', index=False)
        end_time=time.time()
        return code,'time',end_time-start_time
    else:
        return code,'no data'

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
                print(file)
                data=pd.read_csv(os.path.join(rawdata_folder,f'{file}.txt'), sep="\t", header=0)
                df = pd.DataFrame(data)
                quantity=row=df.shape[0]
                new_row={'code_num': file, 'quantity': quantity}
                dbf = pd.concat([dbf, pd.DataFrame([new_row])])
    dbf.to_csv(os.path.join(os.path.dirname(rawdata_folder),'data_base.txt'), index=False)
    print(len(dbf))
    return dbf

#drawing the fig from the files
def drawing_fig_files(folder_path):
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

    dbf=Database(folder_path)
    dbf.set_index('code_num', inplace=True)
    quantity=0

    files=check_data(folder_path)
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
    # 使用 tabula 讀取 PDF 文件中的表格數據
    tables = tabula.read_pdf(pdf_path, pages="all")
    # 將每個表格轉換為列表
    table_data = []
    for table in tables:
        table_data.append(table.values.tolist())
    table_data=np.vstack(table_data)
    target_stock = []
    # 遍歷表格數據中的每個元素
    for row in table_data:
        for cell in row:
            # 如果元素是數字，則將其添加到數字列表中
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