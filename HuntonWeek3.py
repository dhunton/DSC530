# -------------------------------
# DSC 530: EDA
# Week 3: Programming Assignment
# Due Date: 3/29/20
# Author: Deborah Hunton
#
# Purposes 
# - Read in data from National Survey of Family Growth (FemResp and FemPreg data specifically)
# - Clean  up the data (review generally to make sure accurately imported and cleaned)
# - Evaluate data:
#    a. Are first babies born late? (histogram? – make sure nan variables ignored, only count live births)
#    b. Are first babies heavier or lighter?
# -------------------------------

#import packages per author's code
from __future__ import print_function, division

def CleanFemPreg(df):

    #This is the book author's function to clean Preg data
    
    #mother's age is encloded in centiyears; convert to years
    df.agepreg /= 100.00
    
    #birthwgt_lb contains at least one bogus value (51 lbs)
    #replace with NaN
    df.loc[df.birthwgt_lb > 20, 'birthwgt_lb'] = np.nan
    
    #replace 'not ascertained', 'refused', 'don't know' with NaN
    na_vals = [97, 98, 99]
    df.birthwgt_lb.replace(na_vals, np.nan, inplace=True)
    df.birthwgt_oz.replace(na_vals, np.nan, inplace=True)
    df.hpagelb.replace(na_vals, np.nan, inplace=True)
    
    #replace other not-valid responses for sex, # living
    df.babysex.replace([7,9], np.nan, inplace=True)
    df.nbrnaliv.replace([9], np.nan, inplace=True)
    
    #birthweigth is stored in 2 columns (lbs and oz)
    #convert to single column in pounds
    df['totalwgt_lb']=df.birthwgt_lb + df.birthwgt_oz/16.0
    
    #due to a bug in ReadStatDct, the last variable gets clipped,
    #set to NaN
    df.cmintvw = np.nan

def ReadFemPreg(dct_file='2002FemPreg.dct',
                dat_file='2002FemPreg.dat.gz'):

    #This is the book author's function to read in Preg data
    
    dct=thinkstats2.ReadStataDct(dct_file)
    df=dct.ReadFixedWidth(dat_file, compression='gzip')
    CleanFemPreg(df)
    return df

def CleanFemResp(df):
    pass

def ReadFemResp(dct_file='2002FemResp.dct', 
                dat_file='2002FemResp.dat.gz',
                nrows=None):
    
    #This is the book author's function to read in Resp data
    dct = thinkstats2.ReadStataDct(dct_file)
    df = dct.ReadFixedWidth(dat_file, compression='gzip',
                            nrows=nrows)
    CleanFemResp(df)
    return df

def MakePregMap(df):
    
    #This is the book author's function
    d = defaultdict(list)
    for index, caseid in df.caseid.iteritems():
        d[caseid].append(index)
    return d

def ValidatePregnum(resp, preg):
    
    #This is the book author's function to double-check
    preg_map = MakePregMap(preg)
    for index, pregnum in resp.pregnum.iteritems():
        caseid = resp.caseid[index]
        indices = preg_map[caseid]
        if len(indices) != pregnum:
            print(caseid, len(indices), pregnum)
            return False
    return True

def exercise_1_1(resp, preg):
    #Select the birthord column, print the value counts
    #compare to results in codebook
    vc = preg.birthord.value_counts().sort_index()
    print(vc)
    
    #Use isnull to count the number of nans
    num_nulls = preg.birthord.isnull().sum()
    print("The number of nulls is: ", num_nulls)
    
    #Select the prglngth column, print the value counts
    #compare to results in codebook
    vc = preg.prglngth.value_counts().sort_index()
    print(vc)
    
    #Compute the mean of birthweight in pounds
    mn = preg.totalwgt_lb.mean()
    print("The mean of the weights in lb is: ", mn)
    
    #Create new column named totalwgt_kg, compute mean
    preg['totalwgt_kg']=preg.totalwgt_lb / 2.2046223
    mn = preg.totalwgt_kg.mean() 
    print("The mean of the weights in kg is: ", mn)
    
    #Select the age_r column from resp and print value counts
    #How old are oldest and youngest respondents?
    vc = resp.age_r.value_counts().sort_index()
    print(vc)
    old = max(resp.age_r)
    young = min(resp.age_r)
    print("The oldest respondent was ", old, " years old.")
    print("The youngest respondent was ", young, " years old.")
    
    #How old is the respondent with caseid 1?
    check_age = resp.loc[resp.caseid==1,'age_r'].tolist()
    print("Respondent #1 was ", check_age[0], " years old.")
    
    #What are the pregnancy lengths for the respondent 
    #with caseid 2298
    pregnancy_lengths = preg.loc[(preg.caseid==2298) & (preg.outcome==1), 
                                 'prglngth'].tolist()
    print("The pregnancy lengths for respondent #2298 are ", 
          pregnancy_lengths)
    
    #What was the birthweight of the 1st baby born
    #to the respondent with caseid 5012
    first_baby_wt = preg.loc[(preg.caseid==5012) & (preg.pregordr==1)
                      & (preg.outcome==1), 'totalwgt_lb'].tolist()
    print("The weight of the first baby for respondent #5012 was ", 
          first_baby_wt[0], ".")

def exercise_2_4(resp, preg):
    #Using the variable totalwgt_lb, investigate whether
    #first babies are lighter or heavier than others.
    
    #All babies
    preg['totalwgt_lb'].hist(bins=100)
    
    #First babies
    first_babies = preg[(preg.pregordr==1) &
                        (preg.outcome==1)].totalwgt_lb.values.tolist()
    first_babies_wt = [float(kid) for kid in first_babies 
                       if not(pd.isnull(kid))]
    plt.hist(first_babies_wt, bins=100)
    plt.show()
    
    #All other babies
    other_babies = preg[(preg.pregordr!=1) &
                        (preg.outcome==1)].totalwgt_lb.values.tolist()
    other_babies_wt = [float(kid) for kid in other_babies
                       if not(pd.isnull(kid))]
    plt.hist(other_babies_wt, bins=100)
    plt.show()   
    
    #Compute Cohen's d to qualify the difference between
    #the groups. How does it compare to the difference
    #in pregnancy length?

    mean1 = np.mean(first_babies_wt)
    mean2 = np.mean(other_babies_wt)
    var1 = np.var(first_babies_wt)
    var2 = np.var(other_babies_wt)
    n1 = len(first_babies_wt)
    n2 = len(other_babies_wt)
    cohen_d = (mean1 - mean2) / (((n1*var1) + (n2*var2)) / (n1 + n2))
    print("Cohen's d for first vs other babies is: ", cohen_d)
    

def main():
    resp=ReadFemResp()
    assert(len(resp) == 7643)
    assert(resp.pregnum.value_counts()[1] == 1267)
    
    preg = ReadFemPreg()
    print(preg.shape)
    
    assert len(preg) == 13593
    assert preg.caseid[13592] == 12571
    assert preg.pregordr.value_counts()[1] == 5033
    assert preg.nbrnaliv.value_counts()[1] == 8981
    assert preg.babysex.value_counts()[1] == 4641
    assert preg.birthwgt_lb.value_counts()[7] == 3049
    assert preg.birthwgt_oz.value_counts()[0] == 1037
    assert preg.prglngth.value_counts()[39] == 4744
    assert preg.outcome.value_counts()[1] == 9148
    assert preg.birthord.value_counts()[1] == 4413
    assert preg.agepreg.value_counts()[22.75] == 100
    assert preg.totalwgt_lb.value_counts()[7.5] == 302
    
    weights = preg.finalwgt.value_counts()
    key = max(weights.keys())
    assert preg.finalwgt.value_counts()[key] == 6
    
    assert(ValidatePregnum(resp, preg))
    
    print('All tests passed.')
    
    exercise_1_1(resp, preg)
    exercise_2_4(resp, preg)


#import packages per author's code
import sys
import numpy as np
import thinkstats2
import matplotlib.pyplot as plt

from collections import defaultdict

#import packages I need for my code
import pandas as pd

if __name__ == "__main__":
    main()

