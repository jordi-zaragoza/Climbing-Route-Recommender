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

@st.cache(allow_output_mutation=True)
def get_grades_instance():
    # Fetch data from URL here, and then clean it up.
    gr = grades()
    return gr

@st.cache(allow_output_mutation=True)
def get_location_instance():
    # Fetch data from URL here, and then clean it up.
    routes = pd.read_csv('../data/routes_rated.csv',low_memory=False, index_col=0)
    loc = location(routes)
    print("Routes shape: ", loc.routes.shape)
    return loc

@st.cache(allow_output_mutation=True)
def get_climber_instance():
    # Fetch data from URL here, and then clean it up.
    cl = climber()
    return cl

# ----------------------------- Other Functions ----------------------------------------
def crags(country, cols):
    
    options = get_location_instance().crags_in_country(country)
    idx = 0
    if len(options)>101:
        idx = 101
        
    crag = cols[1].selectbox(
         label = 'Select crag',
         options = (options),
         index = idx)        
    return crag

def sectors(crag, cols):

    idx = 0    
    options = get_location_instance().sectors_in_crag(crag)
    if len(options)>10:
        idx = 10
    
    sector = cols[2].selectbox(
         label = 'Select sector',
         options = (options),
         index = idx)
    return sector

def display_nice(routes_df):
    routes_nice = routes_df.copy()
    
    gr = get_grades_instance()
    
    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))
    
    routes_nice = routes_nice[['name','grade_fra','rating_tot','cluster','height_plus']]
                               
    st.write(routes_nice)

def display_nice_2(routes_df):
    routes_nice = routes_df.copy()
    
    gr = get_grades_instance()
    
    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))
    
    routes_nice = routes_nice[['name','grade_fra','rating_tot','liked']]
                               
    st.write(routes_nice)

# ----------------------------- Graphical Part ----------------------------------------

st.title('⛰️ Climb Recommender 🧗')

st.markdown("""---""")

st.sidebar.write(
    f"Hi there 👋"
)

st.sidebar.write(
    f"This is the climbing route recomender. My final project for the IronHack Data Analytics bootcamp"
)

st.sidebar.write(
    f"I am sure that there are some things to improve... if you have any ideas or want to colab, feel free to [contact me](https://www.linkedin.com/in/jordi-zaragoza-cuffi/)."
)

st.sidebar.write(
    f"[Github repo](https://github.com/jordi-zaragoza/Climbing-Route-Recommender) for more info about this app."
)

st.sidebar.write(
    f"created by Jordi Zaragoza"
)

# ----------------------- Form -----------------------------------------
def main():

    cols = st.columns(2)
    name = cols[0].text_input('Enter your name', 'Peter')

    height = cols[1].slider('Select your height (cm)', 150, 200, 175)


    cols = st.columns(2)
    grade = cols[0].selectbox(label = 'Select your grade (fra)',
                         options = (get_grades_instance().get_grades_fra()),
                         index = 5)

    grade_r = cols[1].slider('Grade range', 1, 10)
    grade_range = grade_r * 2

    cols = st.columns(3)

    country = cols[0].selectbox(
         label = 'Select the country',
         options = (get_location_instance().all_countries()),
         index = 17)

    crag = crags(country, cols)

    sector = sectors(crag, cols)

    get_climber_instance().set_attributes(name = name,
                                       grade = grade, 
                                       grade_range = grade_range,
                                       location = [country, crag, sector],
                                       height = height)


    st.markdown("""---""")  

    # ----------------------- Recommendation -----------------------------------------

    routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(routes = get_location_instance().routes)
    
    if st.button('Shuffle'):
        print("Routes shape: ", get_location_instance().routes.shape)
        

    # st.header('Sector - ' + sector.capitalize())       
    # display_nice(routes_sector_rec.head(1))   

    route = routes_sector_rec.head(1)



    

    try:
        st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())
        col1, col2, col3 = st.columns(3)
        
        with col1:  
            
            st.title(route.name.values[0].capitalize())
            st.subheader(get_grades_instance().get_fra(round(route.grade_mean.values[0])))  

        with col3:
                
            liked = st.radio("Have you done it?",
                             ('Liked', 'Not liked', 'Meh...'))

            if st.button('Done'):
                if liked == 'Liked':
                    get_climber_instance().add_route_liked(route)
                    get_location_instance().remove_route(route.name_id.values[0])    
                elif liked == 'Not liked':
                    get_climber_instance().add_route_not_liked(route)    
                    get_location_instance().remove_route(route.name_id.values[0])  
                else:
                    get_climber_instance().add_route(route)
                    get_location_instance().remove_route(route.name_id.values[0]) 
                    
                print("Routes shape: ", get_location_instance().routes.shape)

    except:

        st.write("Cannot find any route, try to use another range")

    # with col3:
    #     if st.button('Liked'):
    #         climber_ins.add_route_liked(route)
    #         loc.remove_route(route.name_id.values[0])

    # with col4:
    #     if st.button('Normal'):
    #         climber_ins.add_route(route)
    #         loc.remove_route(route.name_id.values[0])              

    # with col5:
    #     if st.button('Not liked'):
    #         climber_ins.add_route_not_liked(route)    
    #         loc.remove_route(route.name_id.values[0])


    # --- Button ---
    with st.expander('Show me more'):

        routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(routes = get_location_instance().routes)

    #     st.balloons()

        st.header('Sector - ' + sector.capitalize())       
        display_nice(routes_sector_rec.head(5))   

        st.markdown("""---""")        
        st.header('Crag - ' + crag.capitalize())        
        display_nice(routes_crag_rec.head(5)) 

        st.markdown("""---""")
        st.header('Country - '+ country.capitalize())           
        display_nice(routes_country_rec.head(5)) 

        
    # ------------------------- Info -----------------------------------------------

    st.markdown("""---""") 
    
    with st.expander('User Info'):

        st.write('Routes climbed')

        df_routes_climbed = get_climber_instance().get_routes_climbed()
        if df_routes_climbed.shape[0] > 0:
            display_nice_2(df_routes_climbed)

        st.write('Details')

        st.write(get_climber_instance().get_data())
        
        # if st.button('Route search/Routes done'):
        # # with st.expander("Route search"):

        #     routes_sector_all = loc.routes_in_sector(country, crag, sector)

        #     for idx in range(routes_sector_all.shape[0] if routes_sector_all.shape[0] < 5 else 5):

        #         route = routes_sector_all.iloc[[idx]]

        #         col1, col2, col3, col4, col5 = st.columns(5)

        #         with col1:
        #             st.write(route.name.values[0].capitalize())

        #         with col2:
        #             st.write(get_grades_instance().get_fra(round(route.grade_mean.values[0])))

        #         with col3:
        #             if st.button(str(idx)+' Liked'):
        #                 climber_ins.add_route_liked(route)
        #                 loc.remove_route(route.name_id.values[0])

        #         with col4:
        #             if st.button(str(idx)+' Normal'):
        #                 climber_ins.add_route(route)
        #                 loc.remove_route(route.name_id.values[0])              

        #         with col5:
        #             if st.button(str(idx)+' Not liked'):
        #                 climber_ins.add_route_not_liked(route)    
        #                 loc.remove_route(route.name_id.values[0])

        #         st.markdown("""---""")        
        
        
        
if __name__ == "__main__":
    main()
