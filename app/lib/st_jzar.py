import requests
import streamlit as st
from lib.grades_class import Grades
from lib.location_class import Location
from lib.climber_class import Climber
from lib.mongo_jor import load_climber, save_climber, delete_db
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Panel, Tabs, HoverTool
from streamlit_lottie import st_lottie


# ----------------------------- Functions to run once --------------------------------
@st.cache(allow_output_mutation=True)
def get_grades_instance():
    gr = Grades()
    return gr


@st.cache(allow_output_mutation=True)
def get_location_instance():
    routes = pd.read_csv('data/routes_rated.csv', low_memory=False, index_col=0)
    loc = Location(routes)
    print("Routes shape: ", loc.routes.shape)
    return loc


@st.cache(allow_output_mutation=True)
def get_climber_instance(cluster_init_value=None):
    try:
        cl = load_climber(0)
        print("Climber loaded from mongo")

    except:
        cl = Climber(cluster_init=cluster_init_value)
        print("Climber no mongo")

    return cl


# ----------------------------- Sidebar ----------------------------------------
def sidebar():
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


# ----------------------------- Page config ------------------------------------------
def page_config():
    st.set_page_config(
        page_title="Route recommender",
        page_icon="mountain"
    )

    if 'key' not in st.session_state:
        st.session_state['key'] = 1


# ---------------------------- Title -----------------------------------------------
def title():
    col1, col2, col3 = st.columns([5, 2, 5])

    with col1:
        st.write(" ")

    with col2:
        st_lottie(mountain1, key='m1')

    with col3:
        st.write(" ")

    st.markdown("<h1 style='text-align: center; color: black;'>Climb Recommender</h1>", unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")
    st.markdown("""---""")
    st.write(" ")
    st.write(" ")


# ----------------------- Form -----------------------------------------
class User_input:
    def __init__(self):
        self.grade = None
        self.grade_range = None
        self.location = None
        self.height = None
        self.cluster_init_value = None


def button_recommend(user_input):
    if st.button('Recommend!'):
        get_climber_instance().set_attributes(grade=user_input.grade,
                                              grade_range=user_input.grade_range,
                                              location=user_input.location,
                                              height=user_input.height,
                                              cluster_init=user_input.cluster_init_value)

        save_climber(get_climber_instance())


def cluster_selector(cols):
    cluster_init_key = cols[0].selectbox(label='What kind of routes do you prefer', options=cluster_list.values())
    return list(cluster_list.keys())[list(cluster_list.values()).index(cluster_init_key)]


def crags(country, cols, loc):
    options = loc.crags_in_country(country)

    try:
        idx = list(options).index(get_climber_instance().get_data().crag[0])

    except:
        idx = 0

    crag = cols[1].selectbox(
        label='Select crag',
        options=options,
        index=idx)
    return crag


def sectors(crag, cols, loc):
    options = loc.sectors_in_crag(crag)

    try:
        idx = list(options).index(get_climber_instance().get_data().sector[0])

    except:
        idx = 0

    sector = cols[2].selectbox(
        label='Select sector',
        options=options,
        index=idx)
    return sector


def location_selector():
    cols = st.columns(3)

    idx = list(get_location_instance().all_countries()).index(get_climber_instance().get_data().country[0])

    country = cols[0].selectbox(label='Select the country',
                                options=get_location_instance().all_countries(),
                                index=idx)
    crag = crags(country, cols, get_location_instance())
    sector = sectors(crag, cols, get_location_instance())
    return [country, crag, sector]


def get_user_input():
    user_input = User_input

    # ------ First line -------
    cols = st.columns(2)
    user_input.cluster_init_value = cluster_selector(cols)
    user_input.height = cols[1].slider('Select your height (cm)', 150, 200,
                                       int(get_climber_instance().get_data().height[0]))

    # ------ Second line -------
    cols = st.columns(2)
    try:
        idx = get_grades_instance().get_grades_fra().index(get_climber_instance().get_data().grade_fra[0])
    except:
        idx = 0

    user_input.grade = cols[0].selectbox(label='Select your grade (fra)',
                                         options=(get_grades_instance().get_grades_fra()),
                                         index=idx)

    user_input.grade_range = cols[1].slider('Grade range', 1, 10,
                                            int(get_climber_instance().get_data().grade_range[0]) * 2)

    # ------ Third line -------
    user_input.location = location_selector()

    return user_input


def form():
    user_input = get_user_input()

    st.write(" ")
    st.write(" ")

    button_recommend(user_input)

    st.markdown("""---""")
    st.write(" ")
    st.write(" ")


# ----------------------- Recommendation -----------------------------------------
def like_it(liked, route, cl):
    return {
        'Liked': lambda: cl.add_route_liked(route),
        'Not liked': lambda: cl.add_route_not_liked(route)
    }.get(liked, lambda: cl.add_route(route))()


def recommendation():
    routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
        routes=get_location_instance().routes)

    print(routes_sector_rec.shape[0])

    if routes_sector_rec.shape[0] > 0:

        route = routes_sector_rec.head(1)

        c1, c2 = st.columns([4, 1])

        with c2:

            st.write(" ")

            liked = st.radio("Have you done it?", ('Liked', 'Not liked', 'Meh...'))

            if st.button('Done'):
                like_it(liked, route, get_climber_instance())
                get_location_instance().remove_route(route.name_id.values[0])
                save_climber(get_climber_instance())
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_sector_rec.shape[0] > 0:
            with c1:
                route = routes_sector_rec.head(1)
                st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(
                    round(route.grade_mean.values[0])))
                st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())

        else:
            if routes_crag_rec.shape[0] > 0:
                with c1:
                    route = routes_crag_rec.head(1)
                    st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())
                    st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(
                        round(route.grade_mean.values[0])))
                    st.write(" ")
                    st.write(" ")
                    st.write("Cannot find a route in this sector, crag recommendation")

    elif routes_crag_rec.shape[0] > 0:

        route = routes_crag_rec.head(1)

        c1, c2 = st.columns([4, 1])

        with c2:

            liked = st.radio("Have you done it?", ('Liked', 'Not liked', 'Meh...'))

            if st.button('Done'):
                like_it(liked, route, get_climber_instance())
                get_location_instance().remove_route(route.name_id.values[0])
                save_climber(get_climber_instance())
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_crag_rec.shape[0] > 0:
            with c1:
                route = routes_crag_rec.head(1)
                st.subheader(route.crag.values[0].capitalize() + " - " + route.sector.values[0].capitalize())
                st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(
                    round(route.grade_mean.values[0])))
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


# -------------------------- Show me more button ---------------------------------------
def display_nice(routes_df, gr):
    routes_nice = routes_df.copy()
    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))
    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'liked']]
    st.write(routes_nice)


def display_nice_routes(routes_df, gr):
    routes_nice = routes_df.copy()
    routes_nice['grade_fra'] = routes_nice.grade_mean.apply(lambda x: gr.get_fra(round(x)))
    routes_nice = routes_nice[['name', 'grade_fra', 'rating_tot', 'cluster', 'height_plus']]
    routes_nice['cluster'] = routes_nice['cluster'].apply(lambda x: cluster_list[x])
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


def show_me_more():
    with st.expander('Show me more'):
        routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
            routes=get_location_instance().routes)

        st.header('Sector - ' + get_climber_instance().location[2].capitalize())
        display_nice_routes(routes_sector_rec.head(5), get_grades_instance())

        st.markdown("""---""")
        st.header('Crag - ' + get_climber_instance().location[1].capitalize())
        display_nice_crag(routes_crag_rec.head(5), get_grades_instance())

        st.markdown("""---""")
        st.header('Country - ' + get_climber_instance().location[0].capitalize())
        display_nice_country(routes_country_rec.head(5), get_grades_instance())


# ------------------------- Climber Info -----------------------------------------------
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


def climber_info():
    st.markdown("""---""")

    with st.expander('User Info'):

        st.write(" ")
        st.subheader('Routes Climbed')
        st.write(" ")

        df_routes_climbed = get_climber_instance().get_routes_climbed()

        if df_routes_climbed.shape[0] > 0:
            display_nice(df_routes_climbed, get_grades_instance())
        else:
            st.write("No routes introduced yet")

        st.write(" ")
        st.subheader('Details')
        st.write(" ")

        st.write(get_climber_instance().get_data()[['name', 'ascents', 'sector', 'height']])

        st.write(" ")
        st.subheader('Clusters')
        st.write(" ")

        c1, c2, c3 = st.columns([2, 20, 3])

        with c2:
            plot_figures()

    st.markdown("""---""")


# ----------------------- Reset -----------------------------------------
def reset():
    if st.button('Reset'):
        delete_db()
        st.session_state.key += 1
        st.legacy_caching.clear_cache()


# ----------------------- Gifs -----------------------------------------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


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
