#Required file name in `Excel_sheets`
#- 'Aftermarket Target 2024_FINAL.xlsx'
#- 'Excel_sheets/target2023.xlsx'
#- 'Excel_sheets/Query Service Sales 2023 to 2024.xlsx'
#- 'ITUSBS_Service_Report_Cleaned.xlsx'

import pandas as pd
import numpy as np

def clean_data2023(target2023):
    target2023 = target2023.drop(columns=['Unnamed: 16','Unnamed: 15','Unnamed: 17','Unnamed: 18','Unnamed: 19','Unnamed: 20',])
    target2023 = target2023.replace(0, np.nan)
    target2023 = target2023.replace('                                                               -', np.nan)
    target2023 = target2023.dropna()
    target2023 = target2023.astype({'JAN': 'int64', 'FEB': 'int64', 'MAR': 'int64', 'APR': 'int64', 'MAY': 'int64', 'JUN': 'int64', 'JUL': 'int64', 'AUG': 'int64', 'SEP': 'int64', 'OCT': 'int64', 'NOV': 'int64', 'DEC': 'int64'})
    target2023.reset_index(drop=True, inplace=True)
    target2023['CATEGORY'] = target2023['SITE'].apply(lambda x: 301 if 'CSA' in x else 300)
    target2023.rename(columns={'brand':'BRAND'},inplace=True)
    target2023 = target2023.melt(id_vars=['BRANCH', 'BRAND', 'CATEGORY'],
                        value_vars=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
                        var_name='month', value_name='value')
    target2023['month'] = pd.to_datetime(target2023['month'] + '-2023', format='%b-%Y')
    return target2023


def clean_data2024(Targetyear):
    new_header = Targetyear.iloc[0]  
    Targetyear = Targetyear[1:] 
    Targetyear.columns = new_header 
    Targetyear.drop([378,95,191,286],inplace=True)
    Targetyear = Targetyear.replace(0, np.nan)
    Targetyear = Targetyear.dropna()
    Targetyear = Targetyear.astype({'JAN': 'int64', 'FEB': 'int64', 'MAR': 'int64', 'APR': 'int64', 'MAY': 'int64', 'JUN': 'int64', 'JUL': 'int64', 'AUG': 'int64', 'SEP': 'int64', 'OCT': 'int64', 'NOV': 'int64', 'DEC': 'int64', 'TOTAL': 'int64'})
    Targetyear.reset_index(drop=True, inplace=True)
    Targetyear = Targetyear[Targetyear['BRAND']!='ALL']
    Targetyear['CATEGORY'] = Targetyear['CATEGORY'].apply(lambda x: 301 if x in ['GOLD', 'SILVER', 'BLUE', 'SILVER +', 'GOLD +', 'BLUE +'] else 300)
    Targetyear = Targetyear.melt(id_vars=['BRANCH', 'BRAND', 'CATEGORY'],
                      value_vars=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
                      var_name='month', value_name='value')
    Targetyear['month'] = pd.to_datetime(Targetyear['month'] + '-2024', format='%b-%Y')
    return Targetyear

def clean_data_income(big_df):
    big_df = big_df.astype({'whName': 'string'})
    big_df = big_df.dropna(subset=['whName'])
    big_df['whName'] = big_df['whName'].apply(lambda x: x[6:])
    big_df['whName'] = big_df['whName'].str.replace("JAKARTA BRANCH", "JAKARTA", case=False, regex=False)
    big_df['INVOICEDATE'] = pd.to_datetime(big_df['INVOICEDATE'])
    big_df['Revenue amount']=big_df['lineamount']
    big_df['INVOICEDATE']=big_df['INVOICEDATE'].dt.to_period('M')

    return big_df

def fix_date_time(df,column):
  df[column] = pd.to_datetime(df[column],
                              format = '%d-%m-%Y %I:%M:%S:%p',
                              errors='coerce'
                              )

def clean_data_sbs(raw_df):
    raw_df = raw_df.dropna(subset=['Job Created', 'First Responce Time', 'OTW to Site', 'Arrive On Site', 'OTW to Site Final', 'Arrive On Site Final', 'Back To Office', 'Arrive in Branch Office', 'Completed Date'])
    raw_df['ART'] = round((raw_df['Arrive On Site Final'] - raw_df['Job Created']).dt.total_seconds()/60)
    raw_df['MTTR'] = round((raw_df['Back To Office'] - raw_df['Job Created']).dt.total_seconds()/3600)
    raw_df['FRT'] = round((raw_df['First Responce Time'] - raw_df['Job Created']).dt.total_seconds()/60)
    raw_df['Utilization']= (((raw_df['Back To Office']-raw_df['Arrive On Site Final']).dt.total_seconds()/3600)/raw_df['MTTR'])*100
    # Drop column: 'CS Number'
    #raw_df = raw_df.drop(columns=['CS Number','WO Number','Job Created Month','Input Source','Inquiry Source','Aging','Creator Email','Creator Phone','Note','Status Note','Status','Issue','Location','Hour Meter','Serial Number'])
    # Drop column: 'Sl no'
    raw_df = raw_df.drop(columns=['Sl no'])
    # Filter rows based on column: 'Creator Group'
    raw_df = raw_df[raw_df['Creator Group'] == "LEADER"]
    #raw_df['ART'] = raw_df['ART'].apply(lambda x: 1 if x < 4800 else 0)
    #raw_df['MTTR'] = raw_df['MTTR'].apply(lambda x: 1 if x < 140 else 0)
    raw_df['FRT'] = raw_df['FRT'].apply(lambda x: 1 if x < 15 else 0)
    #raw_df['Utilization'] = raw_df['Utilization'].apply(lambda x: 1 if x > 50 else 0)
    raw_df['Unit Status'] = raw_df['Unit Status'].apply(lambda x: 1 if x =="NON WARRANTY" else 0)
    raw_df['FTF'] = raw_df['FTF'].map({'YES': 1, 'NO': 0, '-': np.nan})
    raw_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    raw_df.dropna(subset=['Utilization'])
    raw_df['Branch Support'] = raw_df['Branch Support'].str.replace("HEAD OFFICE", "JAKARTA", case=False, regex=False)

    return raw_df




Target2024 = pd.read_excel('Excel_sheets/Aftermarket Target 2024_FINAL.xlsx')

target2023 = pd.read_excel('Excel_sheets/target2023.xlsx')

income_df=pd.read_excel('Excel_sheets/Query Service Sales 2023 to 2024.xlsx')

sbs_df = pd.read_excel('Excel_sheets/ITUSBS_Service_Report_Cleaned.xlsx')

fix_date_time(sbs_df,'Job Created')
fix_date_time(sbs_df,'First Responce Time')
fix_date_time(sbs_df,'OTW to Site')
fix_date_time(sbs_df,'Arrive On Site')
fix_date_time(sbs_df,'OTW to Site Final')
fix_date_time(sbs_df,'Arrive On Site Final')
fix_date_time(sbs_df,'Back To Office')
fix_date_time(sbs_df,'Arrive in Branch Office')
fix_date_time(sbs_df,'Completed Date')


sbs_df_clean = clean_data_sbs(sbs_df.copy())
sbs_df_clean.to_csv('Documents/SBS_data.csv')

Targetyear_clean = clean_data2024(Target2024.copy())

target2023_clean = clean_data2023(target2023.copy())

income_df_clean = clean_data_income(income_df.copy())
income_df_clean.to_csv('Documents/SalesData.csv')

Target2324 = pd.concat([Targetyear_clean, target2023_clean], ignore_index=True)
Target2324['BRANCH'] = Target2324['BRANCH'].replace('TRANS JAKARTA, KLENDER', 'JAKARTA-TJ')
Target2324['BRANCH'] = Target2324['BRANCH'].replace('MAKASAR', 'MAKASSAR')
Target2324['BRANCH'] = Target2324['BRANCH'].replace('FMC BISM MELAK', 'MELAK')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(['MUARAENIM','PT BUKIT ASAM MUARAENIM','FMC PT BUKIT ASAM MUARAENIM',' MUARAENIM ',' FMC PT BUKIT ASAM MUARAENIM '], 'MUARA ENIM')
Target2324['BRANCH'] = Target2324['BRANCH'].replace([' CILEGON ','CILEGON',' JAKARTA '],'JAKARTA')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' PEKANBARU ','PEKANBARU')
Target2324['BRANCH'] = Target2324['BRANCH'].replace([' KERINCI ','KERINCI'],'JAMBI')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' PALEMBANG ','PALEMBANG')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' SURABAYA ','SURABAYA')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' SEMARANG ','SEMARANG')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' MEDAN ','MEDAN')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' JAMBI ','JAMBI')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' SOROAKO ','SOROAKO')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' TRANS JAKARTA  ','JAKARTA-TJ')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' SAMARINDA ','SAMARINDA')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' MANADO ','MANADO')
Target2324['BRANCH'] = Target2324['BRANCH'].replace(' SOROAKO ','SOROAKO')
Target2324['BRANCH'] = Target2324['BRANCH'].replace('MUARATEWEH','MUARA TEWEH')
Target2324=Target2324.groupby(['BRANCH','CATEGORY','month'])['value'].sum().reset_index()
Target2324.to_csv('Documents/TargetData.csv')