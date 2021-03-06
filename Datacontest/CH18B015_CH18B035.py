#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[2]:


#Importing required libraries
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import time
from datetime import datetime
import pickle as pkl
from geopy.geocoders import Nominatim
import geopy.distance
from sklearn import preprocessing


# In[3]:


bikers=pd.read_csv('/data/bikers.csv')
bikers_network=pd.read_csv('/kaggle/input/prml-data-contest-nov-2020/bikers_network.csv')
bikers_lat_log = pd.read_csv('/kaggle/input/bikerlatlog/locations.csv')


# In[4]:


lat_med = bikers_lat_log['latitude'].median()
log_med = bikers_lat_log['longitude'].median()
bikers_lat_log['latitude'].fillna(bikers_lat_log['latitude'].median(), inplace=True)
bikers_lat_log['longitude'].fillna(bikers_lat_log['longitude'].median(), inplace=True)


# In[5]:


bikers_lat_log = bikers_lat_log.fillna(0)

latitude = []
longitude = []

for ind,row in tqdm(bikers.iterrows()):
    x11 = np.where(bikers_lat_log['biker_id'] == row['biker_id'])
    try:
        latitude.append(bikers_lat_log.iloc[x11[0].item()]['latitude'])
        longitude.append(bikers_lat_log.iloc[x11[0].item()]['longitude'])
    except ValueError:
        latitude.append(lat_med)
        longitude.append(log_med)
    
bikers['latitude'] = latitude
bikers['longitude'] = longitude


# In[6]:


bikers


# In[7]:


time_zone = []
for index in tqdm(bikers.index):
    biker_id = bikers.iloc[index]['biker_id']
    time = bikers.iloc[index]['time_zone']
    area = bikers.iloc[index]['area']
    location_id = bikers.iloc[index]['location_id']
    if np.isnan(time):
        if area == 'Epsom':
            time_zone.append(60)
        elif str(area)=='nan':
            if location_id=='FR':
                time_zone.append(60)
            elif location_id == 'US':
                time_zone.append(-240) 
            else:
                time_zone.append(330)
        else:
            if 'Yogyakarta' in area:
                time_zone.append(420)
            elif 'Los Angeles' in area:
                time_zone.append(-480)
            elif 'Abuja' in area:
                time_zone.append(60)
            elif 'London' in area:
                time_zone.append(60)
            elif 'Sigli  Aceh' in area:
                time_zone.append(420)
            elif 'San Francisco' in area:
                time_zone.append(-420)
            elif 'Liverpool' in area:
                time_zone.append(240)
            else:
                time_zone.append(-420)
                
    else:
        time_zone.append(time)
        


# In[8]:


biker_bornIn = []
biker_member_since_day = []
biker_member_since_month = []
biker_member_since_year = []
fmt = '%d-%m-%Y'
biker_gender=[]
for index in tqdm(bikers.index):
    mdate = bikers.iloc[index]['member_since']
    byear= bikers.iloc[index]['bornIn']
    gender=bikers.iloc[index]['gender']
    if byear.isnumeric():
        biker_bornIn.append(int(byear))
    else:
        biker_bornIn.append(1952)
    if mdate== '--None' or str(mdate)=="nan":
        mdate="30-10-2012"
    if gender==None or str(gender)=='nan':
        biker_gender.append('male')
    else:
        biker_gender.append(gender)
    dt = datetime.strptime(mdate, fmt)
    biker_member_since_day.append(dt.day)
    biker_member_since_month.append(dt.month)
    biker_member_since_year.append(dt.year)


# In[9]:


bikers['member_since_day'] = biker_member_since_day
bikers['member_since_month'] = biker_member_since_month
bikers['member_since_year'] = biker_member_since_year
bikers['gender']=biker_gender
bikers['time_zone']=time_zone
bikers['bornIn']=biker_bornIn


# In[10]:


bikers.info()


# In[11]:


bikers_network.info()


# In[12]:


ct=[]
for ind,row in bikers_network.iterrows():
    vals=str(row['friends']).split()
    ct.append(len(vals))
bikers_network['count']=ct


# In[13]:


new=pd.merge(bikers,bikers_network,on=['biker_id'])


# In[14]:


new=pd.get_dummies(new, columns=['gender'])
label_encoder = preprocessing.LabelEncoder() 

new['language_id']= label_encoder.fit_transform(new['language_id']) 
new['location_id']= label_encoder.fit_transform(new['location_id']) 


# In[15]:


bikers.head()


# In[16]:


new=new.drop(['member_since','area'],axis=1)


# In[17]:


new.to_csv('/kaggle/working/feature_extracted_bikers.csv',index=False)


# Now preprocessing tours

# In[18]:


tours=pd.read_csv('/kaggle/input/prml-data-contest-nov-2020/tours.csv')


# In[19]:


X= tours.copy()
X=X.drop(['tour_id','biker_id','tour_date','city','state','pincode','country','latitude','longitude', 'w_other'],axis=1)

X = X.rename(columns=lambda x: int(x[1:])) 


# In[20]:


tours['w_class'] = X.idxmax(axis=1) 


# In[21]:


def select_columns(data_frame, column_names):
    new_frame = data_frame.loc[:, column_names]
    return new_frame

selected_columns = list(tours.columns)
tours = select_columns(tours, selected_columns)


# In[22]:


# acquiant = tours[['tour_id', 'biker_id']]
# tours=tours.drop(['biker_id'],axis=1)
tours = tours.rename(columns={"biker_id": "org_id"})


# In[23]:


tours


# In[24]:


train=pd.read_csv('/kaggle/input/prml-data-contest-nov-2020/train.csv')
train.head()


# In[25]:


train_rate = train[["tour_id", "invited", "like", "dislike"]]
train_rate = train_rate.groupby(by=["tour_id"], as_index=False).sum()
train_rate = train_rate.rename(columns={"invited": "total_invites", "like": "total_likes", "dislike" : "total_dislikes"})
train = pd.merge(train,train_rate,on='tour_id')


# In[26]:


train=pd.merge(train,tours,on='tour_id')


# In[27]:


##This feature extraction should be used in test.csv also
tour_day = []
tour_month = []
tour_year = []
tour_latitude = []
tour_longitude = []
locator = Nominatim(user_agent='myGeocoder')
format = '%d-%m-%Y'

lat_med = train['latitude'].median()
log_med = train['longitude'].median()

for index in tqdm(train.index):
    date = train.iloc[index]['tour_date']
    cty = train.iloc[index]['city']
    stt = train.iloc[index]['state']
    ctry = train.iloc[index]['country']
    ltt = train.iloc[index]['latitude']
    lgt = train.iloc[index]['longitude']
    
    address = ''
    if isinstance(cty, str):
        address += (cty + ',')
    if isinstance(stt, str):
        address += (stt + ',')
    if isinstance(ctry, str):
        address += ctry

    if np.isnan(ltt) or np.isnan(lgt):
        if address:
            try:
                loc = locator.geocode(address)
                tour_latitude.append(loc.latitude)
                tour_longitude.append(loc.longitude)
            except:
                tour_latitude.append(lat_med)
                tour_longitude.append(log_med)

        else:
            tour_latitude.append(lat_med)
            tour_longitude.append(log_med)
    else:
        tour_latitude.append(ltt)
        tour_longitude.append(lgt)
        
    dt = datetime.strptime(date, format)
    tour_day.append(dt.day)
    tour_month.append(dt.month)
    tour_year.append(dt.year)


# In[28]:


train['tour_day'] = tour_day
train['tour_month'] = tour_month
train['tour_year'] = tour_year
train['tour_latitude'] = tour_latitude
train['tour_longitude'] = tour_longitude


# In[29]:


train


# In[30]:


train['timestamp']=pd.to_datetime(train['timestamp'])
train['tour_date']=pd.to_datetime(train['tour_date'])

train['days_gap'] = [(train.iloc[i]['tour_date']-train.iloc[i]['timestamp']).days for i in range(train.shape[0])]
train['seconds_gap'] = [(train.iloc[i]['tour_date']-train.iloc[i]['timestamp']).total_seconds() for i in range(train.shape[0])]


# In[31]:


train=train.dropna(axis=1)


# In[32]:


train.info()


# In[33]:


train =pd.merge(train,new,on='biker_id')


# In[34]:


train['age'] = [(train.iloc[i]['tour_year']-train.iloc[i]['bornIn']) for i in range(train.shape[0])]


# In[35]:


train


# In[36]:


tour_dist = []

for ind,row in tqdm(train.iterrows()):
    coords_1 = (train.iloc[ind]['tour_latitude'], train.iloc[ind]['tour_longitude'])
    coords_2 = (train.iloc[ind]['latitude'], train.iloc[ind]['longitude'])
    tour_dist.append(geopy.distance.distance(coords_1, coords_2).miles)

train['tour_distance'] = tour_dist


# In[37]:


tour_convoy=pd.read_csv('/kaggle/input/prml-data-contest-nov-2020/tour_convoy.csv')


# In[38]:


tour_convoy=tour_convoy.fillna("")
tour_convoy.head()


# In[39]:


num_friends_going = []
num_friends_notgoing = []
num_friends_maybe = []
num_friends_invited = []
tour_going = []
tour_notgoing = []
tour_maybe = []
tour_invited = []
org_acquiant = []

for ind,row in tqdm(train.iterrows()):
    frnds_set=set(row['friends'].split())
    x11=np.where(tour_convoy['tour_id']==row['tour_id'])
    set_org = set(row['org_id'])
    set_going=set(tour_convoy.iloc[x11[0].item()]['going'].split())
    set_notgoing=set(tour_convoy.iloc[x11[0].item()]['not_going'].split())
    set_invited=set(tour_convoy.iloc[x11[0].item()]['invited'].split())
    set_maybe=set(tour_convoy.iloc[x11[0].item()]['maybe'].split())
    org_acquiant.append(len(frnds_set.intersection(set_org)))
    num_friends_going.append(len(frnds_set.intersection(set_going)))
    num_friends_notgoing.append(len(frnds_set.intersection(set_notgoing)))
    num_friends_invited.append(len(frnds_set.intersection(set_invited)))
    num_friends_maybe.append(len(frnds_set.intersection(set_maybe)))
    tour_going.append(len(set_going))
    tour_notgoing.append(len(set_notgoing))
    tour_invited.append(len(set_invited))
    tour_maybe.append(len(set_maybe))


# In[40]:


train['acquaint_org'] = org_acquiant
train=train.drop(['org_id'],axis=1)
train['friends_going']=num_friends_going
train['friends_notgoing']=num_friends_notgoing
train['friends_invited']=num_friends_invited
train['friends_maybe']=num_friends_maybe
train['tour_going'] = tour_going
train['tour_notgoing'] = tour_notgoing
train['tour_maybe'] = tour_maybe
train['tour_invited'] = tour_invited


# In[41]:


processed_train = train
train.to_csv('/kaggle/working/processed_train.csv',index=False)


# In[42]:


test=pd.read_csv('/kaggle/input/prml-data-contest-nov-2020/test.csv')

total_likes = []
total_dislikes = []
total_invites = []

for ind,row in tqdm(test.iterrows()):
    x11 = np.where(train_rate['tour_id'] == row['tour_id'])
    try:
        total_likes.append(train_rate.iloc[x11[0].item()]['total_likes'])
        total_dislikes.append(train_rate.iloc[x11[0].item()]['total_dislikes'])
        total_invites.append(train_rate.iloc[x11[0].item()]['total_invites'])
    except ValueError:
        total_likes.append(0)
        total_dislikes.append(0)
        total_invites.append(0)
    
test['total_invites'] = total_invites
test['total_likes'] = total_likes
test['total_dislikes'] = total_dislikes

# for ind,row in tqdm(test.iterrows()):
#     frnds_set=set(row['friends'].split())
#     x11=np.where(tour_convoy['tour_id']==row['tour_id'])
test=pd.merge(test,tours,on='tour_id')


# In[43]:


tour_day = []
tour_month = []
tour_year = []
tour_latitude = []
tour_longitude = []
locator = Nominatim(user_agent='myGeocoder')
format = '%d-%m-%Y'

lat_med = test['latitude'].median()
log_med = test['longitude'].median()

for index in tqdm(test.index):
    date = test.iloc[index]['tour_date']
    cty = test.iloc[index]['city']
    stt = test.iloc[index]['state']
    ctry = test.iloc[index]['country']
    ltt = test.iloc[index]['latitude']
    lgt = test.iloc[index]['longitude']
    
    address = ''
    if isinstance(cty, str):
        address += (cty + ',')
    if isinstance(stt, str):
        address += (stt + ',')
    if isinstance(ctry, str):
        address += ctry

    if np.isnan(ltt) or np.isnan(lgt):
        if address:
            try:
                loc = locator.geocode(address)
                tour_latitude.append(loc.latitude)
                tour_longitude.append(loc.longitude)
            except:
                tour_latitude.append(lat_med)
                tour_longitude.append(log_med)

        else:
            tour_latitude.append(lat_med)
            tour_longitude.append(log_med)
    else:
        tour_latitude.append(ltt)
        tour_longitude.append(lgt)
        
    dt = datetime.strptime(date, format)
    tour_day.append(dt.day)
    tour_month.append(dt.month)
    tour_year.append(dt.year)


# In[44]:


test['tour_day'] = tour_day
test['tour_month'] = tour_month
test['tour_year'] = tour_year
test['tour_latitude'] = tour_latitude
test['tour_longitude'] = tour_longitude


# In[45]:


test['timestamp']=pd.to_datetime(test['timestamp'])
test['tour_date']=pd.to_datetime(test['tour_date'])

test['days_gap'] = [(test.iloc[i]['tour_date']-test.iloc[i]['timestamp']).days for i in range(test.shape[0])]
test['seconds_gap'] = [(test.iloc[i]['tour_date']-test.iloc[i]['timestamp']).total_seconds() for i in range(test.shape[0])]


# In[46]:


test=test.dropna(axis=1)


# In[47]:


test.info()


# In[48]:


test = pd.merge(test,new,on='biker_id')
test['age'] = [(test.iloc[i]['tour_year']-test.iloc[i]['bornIn']) for i in range(test.shape[0])]


# In[49]:


tour_dist = []

for ind,row in tqdm(test.iterrows()):
    coords_1 = (test.iloc[ind]['tour_latitude'], test.iloc[ind]['tour_longitude'])
    coords_2 = (test.iloc[ind]['latitude'], test.iloc[ind]['longitude'])
    tour_dist.append(geopy.distance.distance(coords_1, coords_2).miles)

test['tour_distance'] = tour_dist


# In[50]:


num_friends_going = []
num_friends_notgoing = []
num_friends_maybe = []
num_friends_invited = []
tour_going = []
tour_notgoing = []
tour_maybe = []
tour_invited = []
org_acquiant = []

for ind,row in tqdm(test.iterrows()):
    frnds_set=set(row['friends'].split())
    x11=np.where(tour_convoy['tour_id']==row['tour_id'])
    set_org = set(row['org_id'])
    set_going=set(tour_convoy.iloc[x11[0].item()]['going'].split())
    set_notgoing=set(tour_convoy.iloc[x11[0].item()]['not_going'].split())
    set_invited=set(tour_convoy.iloc[x11[0].item()]['invited'].split())
    set_maybe=set(tour_convoy.iloc[x11[0].item()]['maybe'].split())
    org_acquiant.append(len(frnds_set.intersection(set_org)))
    num_friends_going.append(len(frnds_set.intersection(set_going)))
    num_friends_notgoing.append(len(frnds_set.intersection(set_notgoing)))
    num_friends_invited.append(len(frnds_set.intersection(set_invited)))
    num_friends_maybe.append(len(frnds_set.intersection(set_maybe)))
    tour_going.append(len(set_going))
    tour_notgoing.append(len(set_notgoing))
    tour_invited.append(len(set_invited))
    tour_maybe.append(len(set_maybe))
    


# In[51]:


test['acquaint_org'] = org_acquiant
test=test.drop(['org_id'],axis=1)
test['friends_going']=num_friends_going
test['friends_notgoing']=num_friends_notgoing
test['friends_invited']=num_friends_invited
test['friends_maybe']=num_friends_maybe
test['tour_going'] = tour_going
test['tour_notgoing'] = tour_notgoing
test['tour_maybe'] = tour_maybe
test['tour_invited'] = tour_invited


# In[52]:


processed_test = test
test.to_csv('/kaggle/working/processed_test.csv',index=False)


# In[53]:


processed_train.head()


# In[54]:


processed_test.head()


# In[59]:


import imblearn
from imblearn.over_sampling import ADASYN
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score as ap,roc_auc_score as auc_roc,f1_score,confusion_matrix as cfm,ConfusionMatrixDisplay as cfmdisp
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.model_selection import StratifiedKFold

from collections import Counter
from sklearn.model_selection import KFold
from sklearn.utils import shuffle
from imblearn.over_sampling import SMOTE, SVMSMOTE, BorderlineSMOTE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
from tqdm.notebook import tqdm
import warnings
warnings.filterwarnings("ignore")


# In[60]:


train = processed_train
train=train.drop(['friends','timestamp','tour_date', 'total_likes', 'total_dislikes', 'w_class', 'gender_female'],axis=1)
train['popularity'] = train['tour_going']/(train['tour_notgoing']+train['tour_maybe'] + train['tour_invited'])


# In[61]:


train=train.drop(['biker_id','tour_id','dislike'],axis=1)

X=train.copy()
X=X.drop(['like'],axis=1)
y=train['like'].copy()

train=train.drop(['like'],axis=1)


# In[62]:


Xnew = X
ynew = y

xtr,xval,ytr,yval = train_test_split(Xnew,ynew,test_size=0.25,stratify=ynew,shuffle=True,random_state=3)


# Just Fitting basic models

# In[64]:


params = {
 'max_depth': [8, 10],
 'learning_rate': [.1, .05, .04],
 'n_estimators' : [120, 125, 130]
}

model_xgb = XGBClassifier(objective= 'binary:logistic')
skf = StratifiedKFold(n_splits=3, shuffle = True, random_state = 3)
grid_xgb = GridSearchCV(model_xgb, params, scoring='neg_log_loss', cv=skf.split(xtr,ytr),verbose=5)


# In[65]:


def train_model(model_xgb,params,cv,xtr,ytr,xval,yval):
  grid_xgb=GridSearchCV(model_xgb,params,cv,scoring='neg_log_loss',verbose=5)
  grid_xgb.fit(xtr,ytr)
  print(grid_xgb.best_params_)
  print(grid_xgb.score(xval,yval))
  print(ap(yval,grid_xgb.predict_proba(xval)[:,1]))
  print(auc_roc(yval,grid_xgb.predict_proba(xval)[:,1]))
  return grid_xgb


# In[66]:


grid_xgb.fit(xtr,ytr)


# In[67]:


grid_xgb.best_params_


# In[68]:


print(grid_xgb.score(xval,yval))
print(ap(yval,grid_xgb.predict_proba(xval)[:,1]))
print(auc_roc(yval,grid_xgb.predict_proba(xval)[:,1]))


# In[69]:


test = processed_test
test=test.drop(['friends','timestamp','tour_date','total_likes', 'total_dislikes','w_class','gender_female'],axis=1)
test['popularity'] = test['tour_going']/(test['tour_notgoing']+test['tour_maybe'] + test['tour_invited'])
test=test.drop(['biker_id','tour_id'],axis=1)
ypred_xgb = grid_xgb.predict_proba(test)[:,1]


# In[71]:


test = processed_test

req=pd.DataFrame()
req['biker_id']=test['biker_id']
req['tour_id']=test['tour_id']

req['probability']=ypred_xgb

k = req.copy()

k['biker_id'].nunique()

bikers_df = k.drop_duplicates(subset="biker_id")
bikers_set = np.array(bikers_df["biker_id"])

bikers = []
tours = []
for biker in bikers_set:
    idx = np.where(biker==k["biker_id"])
    tour = k[["tour_id", "probability"]].loc[idx] # for each unique biker in test data get all the events 
    tour.sort_values(by=['probability'], inplace=True, ascending=False)
    tour = list(tour['tour_id'])
    tour = " ".join(tour) # list to space delimited string
    bikers.append(biker)
    tours.append(tour)

sample_submission =pd.DataFrame(columns=["biker_id","tour_id"])
sample_submission["biker_id"] = bikers
sample_submission["tour_id"] = tours
sample_submission.to_csv("/kaggle/working/CH18B015_CH18B035_1.csv",index=False)


# In[ ]:





# In[72]:


params = {
 'num_leaves': [20, 25, 30],
 'learning_rate': [0.1, 0.05, 0.01],
 'n_estimators' : [125, 150, 200]
}

model_lgbm = LGBMClassifier(boosting_type='gbdt', objective= 'binary')

# base=CatBoostClassifier(loss_function='CrossEntropy',verbose=True,task_type="GPU")
skf = StratifiedKFold(n_splits=3, shuffle = True, random_state = 3)
grid_lgbm = GridSearchCV(model_lgbm, params, scoring='neg_log_loss', cv=skf.split(xtr,ytr),verbose=5)


# In[73]:


def train_model(model,params,cv,xtr,ytr,xval,yval):
  grid_lgbm=GridSearchCV(model_lgbm,params,cv,scoring='neg_log_loss',verbose=5)
  grid_lgbm.fit(xtr,ytr)
  print(grid_lgbm.best_params_)
  print(grid_lgbm.score(xval,yval))
  print(ap(yval,grid_lgbm.predict_proba(xval)[:,1]))
  print(auc_roc(yval,grid_lgbm.predict_proba(xval)[:,1]))
  return grid_lgbm


# In[74]:


grid_lgbm.fit(xtr,ytr)


# In[75]:


grid_lgbm.best_params_


# In[76]:


print(grid_lgbm.score(xval,yval))
print(ap(yval,grid_lgbm.predict_proba(xval)[:,1]))
print(auc_roc(yval,grid_lgbm.predict_proba(xval)[:,1]))


# In[78]:


test = processed_test
test=test.drop(['friends','timestamp','tour_date','total_likes', 'total_dislikes','w_class','gender_female'],axis=1)
test['popularity'] = test['tour_going']/(test['tour_notgoing']+test['tour_maybe'] + test['tour_invited'])
test=test.drop(['biker_id','tour_id'],axis=1)
ypred_lgbm=grid_lgbm.predict_proba(test)[:,1]


# In[79]:


test = processed_test

req=pd.DataFrame()
req['biker_id']=test['biker_id']
req['tour_id']=test['tour_id']

req['probability']=ypred_lgbm

k = req.copy()

k['biker_id'].nunique()

bikers_df = k.drop_duplicates(subset="biker_id")
bikers_set = np.array(bikers_df["biker_id"])

bikers = []
tours = []
for biker in bikers_set:
    idx = np.where(biker==k["biker_id"])
    tour = k[["tour_id", "probability"]].loc[idx] # for each unique biker in test data get all the events 
    tour.sort_values(by=['probability'], inplace=True, ascending=False)
    tour = list(tour['tour_id'])
    tour = " ".join(tour) # list to space delimited string
    bikers.append(biker)
    tours.append(tour)

sample_submission =pd.DataFrame(columns=["biker_id","tour_id"])
sample_submission["biker_id"] = bikers
sample_submission["tour_id"] = tours
sample_submission.to_csv('/kaggle/working/CH18B015_CH18B035_2.csv',index=False)

