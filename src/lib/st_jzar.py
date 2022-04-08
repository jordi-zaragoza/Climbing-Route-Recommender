import requests
import streamlit as st
from grades_class import grades
from location_class import location
from climber_class import climber
import pandas as pd


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


def crags(country, cols, loc):
    options = loc.crags_in_country(country)
    idx = 0
    if len(options) > 109:
        idx = 110

    crag = cols[1].selectbox(
        label='Select crag',
        options=options,
        index=idx)
    return crag


def sectors(crag, cols, loc):
    idx = 0
    options = loc.sectors_in_crag(crag)
    if len(options) > 10:
        idx = 5

    sector = cols[2].selectbox(
        label='Select sector',
        options=options,
        index=idx)
    return sector


def display_nice(routes_df, gr):
    routes_nice = routes_df.copy()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]

    st.write(routes_nice)


def display_nice_2(routes_df, gr):
    routes_nice = routes_df.copy()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'liked']]

    st.write(routes_nice)


def display_nice_crag(routes_df, gr):
    routes_nice = routes_df.copy()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'sector', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]

    st.write(routes_nice)


def display_nice_country(routes_df, gr):
    routes_nice = routes_df.copy()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'crag', 'sector', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]

    st.write(routes_nice)


def like_it(liked, route, cl):
    return {
        'Liked': lambda: cl.add_route_liked(route),
        'Not liked': lambda: cl.add_route_not_liked(route)
    }.get(liked, lambda: cl.add_route(route))()


# ----------------------- Gifs -----------------------------------------

escaladora = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_12cye8ob.json')
mountain1 = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_dqn6Dn.json')
