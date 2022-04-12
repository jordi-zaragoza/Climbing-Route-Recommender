from streamlit_lottie import st_lottie
import seaborn as sns
import matplotlib.pyplot as plt
from lib.st_jzar import *

# This is the route recommender script
#
# I created a route recommender based on the features of the routes and the climber.
# by Jordi Zaragoza
#
# - Contact me if you want to colab -
# email: j.z.cuffi@gmail.com
# github: github.com/jordi-zaragoza

# ----------------------------- Page config ------------------------------------------

st.set_page_config(
    page_title="Route recommender",
    page_icon="mountain"
)

if 'key' not in st.session_state:
    st.session_state['key'] = 1

# ----------------------------- Sidebar ----------------------------------------

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

# ---------------------------- Title -----------------------------------------------

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
def main():
    cols = st.columns(2)
    
    # Initial cluster
    cluster_init_key = cols[0].selectbox(label='What kind of routes do you prefer',
                              options=(cluster_list).values())    
    cluster_init_value = list(cluster_list.keys())[list(cluster_list.values()).index(cluster_init_key)]
    print("cluster init number:", cluster_init_value)

    # Height
    height = cols[1].slider('Select your height (cm)', 150, 200, 175)

    # Grade options
    cols = st.columns(2)
    grade = cols[0].selectbox(label='Select your grade (fra)',
                              options=(get_grades_instance().get_grades_fra()),
                              index=5)

    grade_r = cols[1].slider('Grade range', 1, 10, 2)
    grade_range = grade_r * 2

    cols = st.columns(3)

    # Location options
    country = cols[0].selectbox(
        label='Select the country',
        options=(get_location_instance().all_countries()),
        index=17)

    crag = crags(country, cols, get_location_instance())

    sector = sectors(crag, cols, get_location_instance())

    st.write(" ")
    st.write(" ")

    if st.button('Recommend!'):
        get_climber_instance().set_attributes(grade=grade,
                                              grade_range=grade_range,
                                              location=[country, crag, sector],
                                              height=height,
                                              cluster_init = cluster_init_value)

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
                like_it(liked, route, get_climber_instance())
                get_location_instance().remove_route(route.name_id.values[0])
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_sector_rec.shape[0] > 0:
            with col1:
                route = routes_sector_rec.head(1)
                st.title(route.name.values[0].capitalize() + " - " + get_grades_instance().get_fra(
                    round(route.grade_mean.values[0])))
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
                like_it(liked, route, get_climber_instance())
                get_location_instance().remove_route(route.name_id.values[0])
                routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
                    routes=get_location_instance().routes)

        if routes_crag_rec.shape[0] > 0:
            with col1:
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

    with st.expander('Show me more'):

        routes_country_rec, routes_crag_rec, routes_sector_rec = get_climber_instance().route_recommender(
            routes=get_location_instance().routes)

        st.header('Sector - ' + sector.capitalize())
        display_nice(routes_sector_rec.head(5), get_grades_instance())

        st.markdown("""---""")
        st.header('Crag - ' + crag.capitalize())
        display_nice_crag(routes_crag_rec.head(5), get_grades_instance())

        st.markdown("""---""")
        st.header('Country - ' + country.capitalize())
        display_nice_country(routes_country_rec.head(5), get_grades_instance())

# ------------------------- Climber Info -----------------------------------------------

    st.markdown("""---""")

    with st.expander('User Info'):

        st.write(" ")
        st.subheader('Routes Climbed')
        st.write(" ")

        df_routes_climbed = get_climber_instance().get_routes_climbed()

        if df_routes_climbed.shape[0] > 0:
            display_nice_2(df_routes_climbed, get_grades_instance())
        else:
            st.write("No routes introduced yet")

        st.write(" ")
        st.subheader('Details')
        st.write(" ")

        st.write(get_climber_instance().get_data()[['name', 'ascents', 'sector', 'height']])

        st.write(" ")
        st.subheader('Clusters')
        st.write(" ")

        col1, col2, col3 = st.columns([2, 20, 3])

        with col2:
            plot_figures()

    st.markdown("""---""")

    if st.button('Reset'):
        st.session_state.key += 1
        st.legacy_caching.clear_cache()


if __name__ == "__main__":
    main()
