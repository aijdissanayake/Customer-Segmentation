import pandas as pd
import warnings
import datetime as dt
warnings.filterwarnings('ignore')

# data loading
df = pd.read_excel("Online_Retail.xlsx")
print df.head() # print sample data view of loaded data

# data cleaning
df1 = df
df1 = df1[pd.notnull(df1['CustomerID'])] # remove entries with customer id null
df1 = df1[(df1['Quantity']>0)] # remove the negative values in Quantity column
print df1.shape # print sie of cleaned data
print df1.info() # print info of features of cleaned data

# data processing
df1['TotalPrice'] = df1['Quantity'] * df1['UnitPrice'] # Add a column for total price.
NOW = dt.datetime(2011,12,10)
df1['InvoiceDate'] = pd.to_datetime(df1['InvoiceDate']) # convert string to datetime
rfmTable = df1.groupby('CustomerID').agg({'InvoiceDate': lambda x: (NOW - x.max()).days,
                                        'InvoiceNo': lambda x: len(x),  
                                        'TotalPrice': lambda x: x.sum()})

rfmTable['InvoiceDate'] = rfmTable['InvoiceDate'].astype(int)
rfmTable.rename(columns={'InvoiceDate': 'recency', 
                         'InvoiceNo': 'frequency', 
                         'TotalPrice': 'monetary_value'}, inplace=True)

print "RMF Table View"
print rfmTable.head() # print sample view of RFM table

quantiles = rfmTable.quantile(q=[0.25,0.5,0.75]) # spliting the metrics
quantiles = quantiles.to_dict()

    # creating segmented RFM table
segmented_rfm = rfmTable

def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4
    
def FMScore(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1

    # Add segment numbers to the newly created segmented RFM table
segmented_rfm['r_quartile'] = segmented_rfm['recency'].apply(RScore, args=('recency',quantiles,))
segmented_rfm['f_quartile'] = segmented_rfm['frequency'].apply(FMScore, args=('frequency',quantiles,))
segmented_rfm['m_quartile'] = segmented_rfm['monetary_value'].apply(FMScore, args=('monetary_value',quantiles,))
print "Segmented RFM Table"
segmented_rfm.head() # sample view of segmented RFM table

segmented_rfm['RFMScore'] = segmented_rfm.r_quartile.map(str) \
                            + segmented_rfm.f_quartile.map(str) \
                            + segmented_rfm.m_quartile.map(str) # adding combined RFM score
segmented_rfm.head()

    # top 10 customers
print segmented_rfm[segmented_rfm['RFMScore']=='111'].sort_values('monetary_value', ascending=False).head(10)
