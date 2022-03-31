import pandas as pd
import numpy as np
import tables_jor
    

def Route_search(routes_identifier, identifier):
    '''
    This function searches for the routes specified by name or id
    
    input:
    routes_identifier -> the df where we want to search
    identifier -> the name or id we want to search
    
    output:
    a dataframe with the routes filtered
    '''
    if type(identifier) == int:
        return routes_identifier[routes_identifier.name_id == identifier]
    else:
        return routes_identifier[routes_identifier.name == identifier]    
    
    
def Crag_search(routes_identifier, identifier):
    '''
    This function searches for the routes specified by crag or crag_id
    
    input:
    routes_identifier -> the df where we want to search
    identifier -> the name or id of the crag we want to search
    
    output:
    a dataframe with the routes filtered
    '''
    if type(identifier) == int:
        return routes_identifier[routes_identifier.crag_id == identifier]
    else:
        return routes_identifier[routes_identifier.crag == identifier]    
    

def Sector_search(routes_identifier, identifier):
    '''
    This function searches for the routes specified by sector
    
    input:
    routes_identifier -> the df where we want to search
    identifier -> the name or id of the sector we want to search
    
    output:
    a dataframe with the routes filtered
    '''
    if type(identifier) == int:
        return routes_identifier[routes_identifier.sector_id == identifier]
    else:
        return routes_identifier[routes_identifier.sector == identifier]  
    
    
def filter_tall(routes_df, climber_usr, show = False):
    '''
    This function filters a routes table deppending on the climbers height and the tall recommendation of the route
    input:
    - routes_df -> routes dataframe
    - climber_usr -> instance of clibers class
    - show -> shows results
    
    output:
    - returns the df filtered
    
    '''
    cl = climber_usr.get_data()
    df_copy = routes_df.copy()
    
    if (cl.height[0] > 180): # Tall person
        df_copy = df_copy[df_copy.tall_recommend_sum > -1] # filter routes for short people
        df_copy['height_plus'] = df_copy.tall_recommend_sum.apply(lambda x: 1 if  (x > 1) else  0) # we add plus for tall

    elif (cl.height[0] < 170): # Short person 
        df_copy = df_copy[df_copy.tall_recommend_sum < 1] # filter routes for short people
        df_copy['height_plus'] = df_copy.tall_recommend_sum.apply(lambda x: 1 if  (x < -1) else  0) # we add plus for short
        
    else:
        df_copy['height_plus'] = 0 # no plus

    df_copy = df_copy.drop(columns='tall_recommend_sum')
    if show:
        print("df routes: ", df_copy.shape[0])
        
    return df_copy


def filter_grade(routes_df, climber_usr, show = False):
    '''
    This function filters a routes table deppending on the climbers grade
    input:
    - routes_df -> routes dataframe
    - climber_usr -> instance of clibers class
    - show -> shows results
    
    output:
    - returns the df filtered
    
    '''
    cl = climber_usr.get_data()
    df_copy = routes_df.copy()

    min_grade = cl.grade[0] - cl.grade_range[0]
    max_grade = cl.grade[0] + cl.grade_range[0]

    df_copy = df_copy[df_copy.grade_mean < max_grade]
    df_copy = df_copy[df_copy.grade_mean > min_grade]

    if show:
        print("df routes: ", df_copy.shape[0])
        
    return df_copy

def filter_cluster(routes_df, climber_usr, show = False):
    '''
    This function filters a routes table deppending on the climbers cluster order
    input:
    - routes_df -> routes dataframe
    - climber_usr -> instance of clibers class
    - show -> shows results
    
    output:
    - returns the df filtered
    
    '''    
    cl = climber_usr
    df_copy = routes_df.copy()
    
    routes_cluster = pd.DataFrame()
    i = 0
    while (routes_cluster.shape[0] < 3) and (i < cl.num_clusters):
        aux_df = df_copy[df_copy.cluster == cl.get_cluster_order()[i]] 
        routes_cluster = pd.concat([routes_cluster,aux_df]) 
        i = i + 1        

    if show:
        print("df routes: ", df_copy.shape[0])
        
    return routes_cluster

def sex_plus(routes_df, climber_usr, show = False, threshold = 0.1):
    '''
    This function gives a plus for men routes (ratio < threshhold) or women routes (ratio > threshhold)
    input:
    - routes_df -> routes dataframe
    - climber_usr -> instance of clibers class
    - show -> shows results
    
    output:
    - returns the df filtered
    
    '''
    cl = climber_usr.get_data()
    df_copy = routes_df.copy()
    
    if (cl.sex[0] == 0): # Men
        df_copy['sex_plus'] = df_copy.sex_ratio.apply(lambda x: 1 if  (x < threshold) else  0) # we add plus for men

    else: # Women 
        df_copy['sex_plus'] = df_copy.sex_ratio.apply(lambda x: 1 if  (x > threshold) else  0) # we add plus for women


    df_copy = df_copy.drop(columns=['sex_ratio'])
    if show:
        print("df routes: ", df_copy.shape[0])
        
    return df_copy