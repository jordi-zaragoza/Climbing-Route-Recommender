from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiment_analysis_spanish import sentiment_analysis
'''
This library contains the functions that I use to clean the dataframe.

created by Jordi Zaragoza
'''


# ------------ CLEANING METHODS FOR ASCENT TABLE -----------------------------

def Tall_recommend(row, mean_height):
    '''
    This function checks if the route is easy for tall people, so I will create a feature called tall_recomend:
        - Tall gets deffined as higher than average + 5cm / small is avg - 5cm
        - If you are tall and say its soft
        - If you are small and say its hard
        - You get a -1 if the person is high and thinks its hard (this will correct the adding part)
    '''
    
    heigh_dif = row.height - mean_height
    
    if (heigh_dif > 5) and row.soft:
        return 1
    
    if (heigh_dif < -5) and row.hard:
        return 1
    
    if (heigh_dif > 5) and row.hard:
        return -1
    
    if (heigh_dif < -5) and row.soft:
        return -1
        
    return 0   


def Correct_grade_id(df):
    '''
    This function the "id" into the "index" for each grade_id on the ascent table    
    reason: the id is not consecutive so we cannot calculate metrics, like mean..
    '''
    def evaluate(x):
        if x < 48:
            x-1
        elif x < 61:
            x-2
        elif x < 74:
            x-3
        else:
            x-4
        return x
    df['grade_id'] = df['grade_id'].apply(lambda x: evaluate(x))
    return df

def Correct_conversion_table(df):
    '''
    This function removes the unnecessary rows of the conversion table and rearranges the grading
    '''
    aux = df.copy()
    aux = pd.concat([aux.iloc[[0]],aux.iloc[[0]], aux], ignore_index=True)
    aux = aux.reset_index(drop = True).reset_index()
    aux = aux.drop(columns='id')
    aux.columns = ['grade_id','grade_fra']
    
    return aux

def Split_notes(x):
    first_ascent = 0
    second_go = 0 
    soft = 0
    hard = 0 
    traditional = 0
    one_hang = 0
    
    x_str = x.split(', ')
    if "Soft" in x_str:
        soft = 1        
    if "Hard" in x_str:
        hard = 1
    if "Traditional" in x_str:
        traditional = 1
    if "First Ascent" in x_str:
        first_ascent = 1
        
    return first_ascent, soft, hard, traditional

# If a grade is considered hard then +1 if it is considered soft then -1 to the grade_id
def Easy_hard(row):
    x = row.grade_id
    if (row.hard):
        return x+1 
    elif (row.soft):
        return x-1 
    else:
        return x