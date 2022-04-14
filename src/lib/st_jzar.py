import requests
import streamlit as st
from lib.grades_class import Grades
from lib.location_class import Location
from lib.climber_class import Climber
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Panel, Tabs, HoverTool, Range1d


# ----------------------------- Functions to run once --------------------------------


@st.cache(allow_output_mutation=True)
def get_grades_instance():
    gr = Grades()
    return gr


@st.cache(allow_output_mutation=True)
def get_location_instance():
    routes = pd.read_csv('../data/routes_rated.csv', low_memory=False, index_col=0)
    loc = Location(routes)
    print("Routes shape: ", loc.routes.shape)
    return loc


@st.cache(allow_output_mutation=True)
def get_climber_instance(cluster_init_value=None):
    cl = Climber(cluster_init=cluster_init_value)
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

    routes_nice['cluster'] = routes_nice['cluster'].apply(lambda x: cluster_list[x])

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

    routes_nice['cluster'] = routes_nice['cluster'].apply(lambda x: cluster_list[x])

    st.write(routes_nice)


def display_nice_country(routes_df, gr):
    routes_nice = routes_df.copy()

    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))

    routes_nice = routes_nice[['name', 'crag', 'sector', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]

    routes_nice['cluster'] = routes_nice['cluster'].apply(lambda x: cluster_list[x])

    st.write(routes_nice)


def like_it(liked, route, cl):
    return {
        'Liked': lambda: cl.add_route_liked(route),
        'Not liked': lambda: cl.add_route_not_liked(route)
    }.get(liked, lambda: cl.add_route(route))()


def plot_figures():
    lst = get_climber_instance().get_cluster_order()
    lst_updown = [lst[len(lst) - idx - 1] for idx in range(len(lst))]
    order = pd.DataFrame(lst_updown)
    order.reset_index(inplace=True)
    order.columns = ['priority order', 'cluster number']

    hover = HoverTool(
        tooltips=[
            ('Cluster', '$x{0}'),
        ],
    )

    p = figure(
        x_axis_label='Cluster number',
        y_axis_label='Priority order',
        width=500, height=400, tools=[hover])

    p.vbar(x=order["cluster number"], top=order["priority order"], width=0.5)

    p.xaxis.ticker = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    p.yaxis.ticker = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    p.yaxis.major_label_overrides = {
        0: r"Last",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: r"First"
    }

    clusters = pd.DataFrame(get_climber_instance().cluster)
    clusters.reset_index(inplace=True)
    clusters.columns = ['cluster number', 'times liked']

    q = figure(
        x_axis_label='Cluster number',
        y_axis_label='Times liked',
        width=500, height=400, tools=[hover])

    q.vbar(x=clusters["cluster number"], top=clusters["times liked"], width=0.5)

    q.xaxis.ticker = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    q.yaxis.ticker = [-1, 0, 1]

    tab1 = Panel(child=p, title="Priority Order")
    tab2 = Panel(child=q, title="Times liked")

    all_tabs = Tabs(tabs=[tab1, tab2])

    st.bokeh_chart(all_tabs, use_container_width=True)


# ----------------------- Gifs -----------------------------------------


escaladora = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_12cye8ob.json')
mountain1 = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_dqn6Dn.json')

# ----------------------- Cluster types --------------------------------

cluster_list = {2: 'Very Famous',
                8: 'Famous but not so repeated',
                4: 'Very repeated',
                3: 'Very hard',
                0: 'Very soft',
                6: 'Traditional ',
                5: 'Chipped',
                7: 'Easy to On-sight',
                1: 'Routes for some reason preferred by women'}
