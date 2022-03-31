import pandas as pd
import numpy as np
import pickle
import streamlit as st
import climb_jor
from grades_class import grades
from location_class import location
from climber_class import climber

# This is the route recommender script
#
# I created a route recommender based on the features of the routes and the climber.
# by Jordi Zaragoza
#
# - Contact me if you want to colab -
# email: j.z.cuffi@google.com
# github: github.com/jordi-zaragoza

# ----------------------------- Page config ------------------------------------------

st.set_page_config(
    page_title="Route recommender", page_icon="🧗"
)

# ----------------------------- Functions to run once --------------------------------

@st.cache
def get_grades_instance():
    # Fetch data from URL here, and then clean it up.
    gr = grades()
    return gr

@st.cache
def get_location_instance():
    # Fetch data from URL here, and then clean it up.
    routes = pd.read_csv('../data/routes_rated.csv',low_memory=False, index_col=0)
    loc = location(routes)
    return loc

@st.cache
def get_climber_instance(name,grade,grade_range,location,height,sex):
    # Fetch data from URL here, and then clean it up.
    cl = climber(name = None, 
                 grade = 54, 
                 grade_range = 2,
                 location = ['esp', 'montserrat', 'agulla del senglar'], 
                 height = 170, 
                 sex = 0)
    return cl



# ----------------------------- Grafical Part ----------------------------------------

st.title('The Climbing Route Recommender')

# --- Functions -----
def crag(country):
    crag = st.selectbox(
         label = 'Select crag',
         options = (get_location_instance().crags_in_country(country)))
    return crag

def sector(crag):
    sector = st.selectbox(
         label = 'Select crag',
         options = (get_location_instance().sectors_in_crag(crag)))
    return sector

# --- Input text ----
title = st.text_input('Enter your name', 'Peter')

# --- Selector ---
height = st.selectbox(
     label = 'Select your height (cm)',
     options = ([number for number in range(150,200,1)]),
     index = 25)

grade = st.selectbox(
     label = 'Select your grade (fra)',
     options = (get_grades_instance().get_grades_fra()),
     index = 5)

country = st.selectbox(
     label = 'Select the country',
     options = (get_location_instance().all_countries()),
     index = 10)

crag = crag(country)

sector = sector(crag)


# --- Gender Selector ---
gender = st.radio(
     label = "What's your favorite movie genre",
     options = ('Male', 'Female', 'Other'))

if gender == 'Female':
     gender = 1
else:
     gender = 0
       
        
# --- Button ---
if st.button('Fire!'):
    climber_ins = get_climber_instance(name = None,
                                   grade = grade, 
                                   grade_range = 2,
                                   location = [country, crag, sector],
                                   height = height,
                                   sex = gender)
    
    
    routes_country_rec, routes_crag_rec, routes_sector_rec = climber_ins.route_recommender()
    
    st.write(routes_country_rec.head(5))
    st.write(routes_crag_rec.head(5))    
    st.write(routes_sector_rec.head(5))    
