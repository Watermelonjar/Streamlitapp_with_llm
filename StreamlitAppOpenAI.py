from openai import OpenAI
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


st.title("Chat Service data")
st.subheader("powered by GPT")
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Load data
SalesData = pd.read_csv('Documents/SalesData.csv')
SBSData = pd.read_csv('Documents/SBS_data.csv')
TargetData = pd.read_csv('Documents/TargetData.csv')

# Ensure date columns are in datetime format
SalesData["INVOICEDATE"] = pd.to_datetime(SalesData["INVOICEDATE"])
TargetData['month'] = pd.to_datetime(TargetData["month"])

# Define date range for slider
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 6, 30)

# Group sales data and reset index to keep grouped columns as regular columns
salesfinal = SalesData.groupby(['INVOICEDATE', 'BusinessUnit', 'siteName'])['lineamount'].sum().reset_index()

SBSData["Job Created"] = pd.to_datetime(SBSData["Job Created"]).dt.to_period('M').dt.to_timestamp()

# Calculate the mean of the specified columns
SBSfinal_mean = SBSData.groupby(['Branch Support', 'Job Created','Function Group'])[['ART', 'MTTR', 'FTF', 'FRT']].mean().reset_index()

# Calculate the count of each group
SBSfinal_count = SBSData.groupby(['Branch Support', 'Job Created','Function Group']).size().reset_index(name='Count')

# Merge the mean and count dataframes
SBSfinal = pd.merge(SBSfinal_mean, SBSfinal_count, on=['Branch Support', 'Job Created', 'Function Group'])


# Initialize session state variables
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for user inputs
with st.sidebar:
    Sitedata = st.selectbox(label='Select site', options=salesfinal['siteName'].unique())
    daterange = st.slider(
        label='Select Date Range',
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(days=30),
    )
    BusinessUnit = st.selectbox(label='Select Business Unit', options=salesfinal['BusinessUnit'].unique())

# Function to filter sales and target data
def datagiver(site, daterange, business_unit):
    filtered_data = salesfinal[
        (salesfinal['siteName'] == site) & 
        (salesfinal['INVOICEDATE'] >= daterange[0]) & 
        (salesfinal['INVOICEDATE'] <= daterange[1]) &
        (salesfinal['BusinessUnit'] == business_unit)
    ]
    filtered_target = TargetData[
        (TargetData['month'] >= daterange[0]) &
        (TargetData['month'] <= daterange[1]) &
        (TargetData['CATEGORY'] == business_unit) &
        (TargetData['BRANCH'] == site)
    ]
    filteredSBS=SBSfinal[
        (SBSfinal['Job Created']>=daterange[0])&
        (SBSfinal['Job Created']<=daterange[1])&
        (SBSfinal['Branch Support']==site)
    ]
    Baseinfo = f"""
    Based on this provided data about machine service context:  
    Respond fully in indonesian
    This is based on data for {business_unit} business unit (300 for retail, 301 for contract)
    
    This is the performance metric data for services for {site} branch:
    ART is actual response time (in minutes, kpi is 1440 min)
    MTTR is mean time to resolve (in hours, kpi is 120 hours)
    FRT is first response time, 1 if it is under kpi
    FTF is first time finish 1 if first time finish, 0 if not
    use the metrics\n
    
    {filteredSBS.to_string(index=False)}
    
    This is the sales log for {site} branch:\n
    
    {filtered_data.to_string(index=False)}
    
    lineamount is value in rupiah(IDR)\n
    This is the Target data:\n
    
    {filtered_target.to_string(index=False)}

    """
    return Baseinfo

    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
        
    contextprompt = datagiver(Sitedata, daterange, BusinessUnit)
    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content":contextprompt +  prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)