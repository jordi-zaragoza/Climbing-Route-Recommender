import pandas as pd
import streamlit as st
from grades_class import grades
from location_class import location
from climber_class import climber
import requests
from streamlit_lottie import st_lottie
import seaborn as sns
import matplotlib.pyplot as plt
import wx

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

if 'key' not in st.session_state:
    st.session_state['key'] = 1

# ----------------------------- Functions to run once --------------------------------
@st.cache(allow_output_mutation=True)
def get_grades_instance():
    gr = grades()
    return gr


@st.cache(allow_output_mutation=True)
def get_location_instance():
    routes = pd.read_csv('../data/routes_rated.csv', low_memory=False, index_col=0)
    loc = location(routes)
    print("Routes shape: ", loc.routes.shape)
    return loc


@st.cache(allow_output_mutation=True)
def get_climber_instance():
    cl = climber()
    return cl


# ----------------------------- Other Functions ----------------------------------------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
      return None
    return r.json()

def crags(country, cols):
    options = get_location_instance().crags_in_country(country)
    idx = 0
    if len(options) > 101:
        idx = 101

    crag = cols[1].selectbox(
        label='Select crag',
        options=options,
        index=idx)
    return crag


def sectors(crag, cols):
    idx = 0
    options = get_location_instance().sectors_in_crag(crag)
    if len(options) > 10:
        idx = 10

    sector = cols[2].selectbox(
        label='Select sector',
        options=options,
        index=idx)
    return sector


def display_nice(routes_df):
    routes_nice = routes_df.copy()

    gr = get_grades_instance()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]

    st.write(routes_nice)


def display_nice_2(routes_df):
    routes_nice = routes_df.copy()

    gr = get_grades_instance()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'liked']]

    st.write(routes_nice)

# ----------------------- Gifs -----------------------------------------
escaladora = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_12cye8ob.json')
mountain1 = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_dqn6Dn.json')

# ----------------------------- Graphical Part ----------------------------------------

st.sidebar.write(
    f"Hi there 👋"
)

st.sidebar.write(
    f"This is the climbing route recomender. My final project for the IronHack Data Analytics bootcamp"
)

st.sidebar.write(
    f"I am sure that there are some things to improve... if you have any ideas or want to colab, feel free to ["
    f"contact me](https://www.linkedin.com/in/jordi-zaragoza-cuffi/). "
)

st.sidebar.write(
    f"[Github repo](https://github.com/jordi-zaragoza/Climbing-Route-Recommender) for more info about this app."
)

st.sidebar.write(
    f"created by Jordi Zaragoza"
)

col1, col2, col3 = st.columns([1, 5, 1])

app = wx.App(False)
width, height = wx.GetDisplaySize()

if (width > height):

    print("computer")
    with col1:
        st.write(" ")
        st_lottie(mountain1, key='m1')

    with col2:
        st.markdown("<h1 style='text-align: center; color: black;'>Climb Recommender</h1>", unsafe_allow_html=True)

    with col3:
        st.write(" ")
        st_lottie(mountain1, key='m2')
else:
    print("phone")

    with col2:
        st.markdown("<h1 style='text-align: center; color: black;'>Climb Recommender</h1>", unsafe_allow_html=True)


# st.write(" ")
# st_lottie(mountain1, key='m1')
# st.markdown("<h1 style='text-align: center; color: black;'>Climb Recommender</h1>", unsafe_allow_html=True)
# st.write(" ")
# st_lottie(mountain1, key='m2')

st.write(" ")
st.markdown("""---""")
st.write(" ")
st.write(" ")

# ----------------------- Form -----------------------------------------
def main():

    cols = st.columns(2)
    name = cols[0].text_input('Enter your name', 'Peter')

    height = cols[1].slider('Select your height (cm)', 150, 200, 175)

    cols = st.columns(2)
    grade = cols[0].selectbox(label='Select your grade (fra)',
                              options=(get_grades_instance().get_grades_fra()),
                              index=5)

    grade_r = cols[1].slider('Grade range', 1, 10, 2)
    grade_range = grade_r * 2

    cols = st.columns(3)

    country = cols[0].selectbox(
        label='Select the country',
        options=(get_location_instance().all_countries()),
        index=17)

    crag = crags(country, cols)

    sector = sectors(crag, cols)

    get_climber_instance().set_attributes(name=name,
                                          grade=grade,
                                          grade_range=grade_range,
                                          location=[country, crag, sector],
                                          height=height)

    st.write(" ")
    st.write(" ")
    st.markdown("""---""")
    st.write(" ")
    st.write(" ")

    # ----------------------- Recommendation -----------------------------------------

    routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
        routes=get_location_instance().routes)

    print(routes_sector_rec.shape[0])

    if routes_sector_rec.shape[0] > 0:

        route = routes_sector_rec.head(1)

        col1, col2 = st.columns([4, 1])

        with col2:

            st.write(" ")

            liked = st.radio("Have you done it?", ('Liked', 'Not liked', 'Meh...'))

            if st.button('Done'):
                if liked == 'Liked':
                    get_climber_instance().add_route_liked(route)

                elif liked == 'Not liked':
                    get_climber_instance().add_route_not_liked(route)
                else:
                    get_climber_instance().add_route(route)

                get_location_instance().remove_route(route.name_id.values[0])
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_sector_rec.shape[0] > 0:
            with col1:
                route = routes_sector_rec.head(1)
                st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(round(route.grade_mean.values[0])))
                st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())

        else:
            if routes_crag_rec.shape[0] > 0:
                with col1:
                    route = routes_crag_rec.head(1)
                    st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())
                    st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(
                        round(route.grade_mean.values[0])))
                    st.write(" ")
                    st.write(" ")
                    st.write("Cannot find a route in this sector, crag recommendation")

    elif routes_crag_rec.shape[0] > 0:
        print("crag")
        route = routes_crag_rec.head(1)

        col1, col2 = st.columns([4, 1])

        with col2:

            liked = st.radio("Have you done it?", ('Liked', 'Not liked', 'Meh...'))

            if st.button('Done'):
                if liked == 'Liked':
                    get_climber_instance().add_route_liked(route)

                elif liked == 'Not liked':
                    get_climber_instance().add_route_not_liked(route)
                else:
                    get_climber_instance().add_route(route)

                get_location_instance().remove_route(route.name_id.values[0])
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_crag_rec.shape[0] > 0:
            with col1:
                route = routes_crag_rec.head(1)
                st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())
                st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(round(route.grade_mean.values[0])))
                st.write(" ")
                st.write(" ")
                st.write("Cannot find a route in this sector, crag recommendation")
    else:
        st.write("Cannot find any route, try to use a wider grade range")

    st.write(" ")
    st.markdown("""---""")
    st.write(" ")
    st.write(" ")

    st_lottie(escaladora, key='c1')

    st.markdown("""---""")
    st.write(" ")

    # --- Button ---
    with st.expander('Show me more'):

        routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
            routes=get_location_instance().routes)

        st.header('Sector - ' + sector.capitalize())
        display_nice(routes_sector_rec.head(5))

        st.markdown("""---""")
        st.header('Crag - ' + crag.capitalize())
        display_nice(routes_crag_rec.head(5))

        st.markdown("""---""")
        st.header('Country - ' + country.capitalize())
        display_nice(routes_country_rec.head(5))

    # ------------------------- Info -----------------------------------------------

    st.markdown("""---""")

    with st.expander('User Info'):

        st.write(" ")
        st.subheader('Routes Climbed')
        st.write(" ")

        df_routes_climbed = get_climber_instance().get_routes_climbed()
        if df_routes_climbed.shape[0] > 0:
            display_nice_2(df_routes_climbed)
        else:
            st.write("No routes introduced yet")

        st.write(" ")
        st.subheader('Details')
        st.write(" ")

        st.write(get_climber_instance().get_data()[['name', 'ascents', 'sector', 'height']])

        st.write(" ")
        st.subheader('Clusters priority')
        st.write(" ")

        col1, col2, col3 = st.columns([2,20,3])

        with col2:

            order = pd.DataFrame(get_climber_instance().get_cluster_order())
            order.reset_index(inplace=True)
            order.columns = ['priority order', 'cluster number']

            fig = plt.figure(figsize=(6, 2))
            sns.barplot(x="cluster number", y="priority order", data=order)
            st.pyplot(fig)



    st.markdown("""---""")


    if st.button('Reset'):
        st.session_state.key += 1
        st.legacy_caching.clear_cache()


if __name__ == "__main__":
    main()
