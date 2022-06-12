import pandas as pd
from lib import clean_jor


def conversion_table():
    """
    this function gets the conversion table from the database and returns it as a df
    """
    conversion_df = pd.read_csv('data/grade.csv')
    conversion_df = conversion_df[['id', 'fra_routes']]
    conversion_df.reset_index(inplace=True)
    return conversion_df


# ----------------------------- GET ROUTES TABLES ----------------------------------------------------------- 

def Get_routes(df):
    """
    This function creates the ROUTES table that will be used for recomending.

        - Groups routes by names
        - Correct the naming
        - Regroup with correct names
        - Filters
        - Asigns an Id to each route

    input:
    df -> the df that we want to clean

    output:
    routes_identifier -> the dataframe with route names, crag, sector, country

    routes_features -> the dataframe with the important recomender features of each route.

    The fetatures for the route reacomender will be:
        - 'sector_id'
        - 'ascents_count'
        - 'grade_median'
        - 'comment_count'
        - 'rating_mean'
        - 'repeat_count'
        - 'recommend_count'
        - 'chiped_count'
        - 'soft_count'
        - 'hard_count'
        - 'traditional_count'
    """

    # Grouping Part ---------------------------------------------------------------------

    # group by route name
    ascent_df6 = df.copy()
    ascent_df6 = ascent_df6.groupby(['country', 'sector_id', 'name']).agg(
        sector=('sector', pd.Series.mode),
        crag=('crag', pd.Series.mode),
        ascents_count=('grade_id', 'count'),
        grade_median=('grade_id', 'median'),
        comment_count=('comment_bool', 'sum'),
        rating_mean=('rating', 'mean'),
        repeat_count=('repeat', 'sum'),
        recommend_count=('user_recommended', 'sum'),
        chiped_count=('chipped', 'sum'),
        soft_count=('soft', 'sum'),
        hard_count=('hard', 'sum'),
        traditional_count=('traditional', 'sum'),
        tall_recommend=('tall_recommend', 'sum'),
        sentiment_count=('sentiment', 'sum'))

    ascent_df6.reset_index(inplace=True)

    # correct route names by string proximity
    # this will replace the names by proximity for the same sectors (not including numbers like: route 1, route 2)
    ascent_df8 = ascent_df6.copy()
    sectors = ascent_df8.sector_id.value_counts().index
    for idx, sector in enumerate(sectors):
        if ((float(idx) / len(sectors)) * 1000) % 1 == 0:
            print("\r{0}".format((float(idx) / len(sectors)) * 100))

        names = ascent_df8[ascent_df8.sector_id == sector].name.values
        idx = ascent_df8[ascent_df8.sector_id == sector].name.index
        names = clean_jor.Similar_array(names, 0.9)
        ascent_df8.loc[idx, "name"] = names

    ascent_df8.to_csv('data/check.csv')

    # We group again
    # multiple columns
    ascent_df9 = ascent_df8.copy()
    ascent_df9 = ascent_df9.groupby(['country', 'sector_id', 'name']).agg(
        sector=('sector', pd.Series.mode),
        crag=('crag', pd.Series.mode),
        ascents_count=('ascents_count', 'sum'),
        grade_median=('grade_median', 'median'),
        comment_count=('comment_count', 'sum'),
        rating_mean=('rating_mean', 'mean'),
        repeat_count=('repeat_count', 'sum'),
        recommend_count=('recommend_count', 'sum'),
        chiped_count=('chiped_count', 'sum'),
        soft_count=('soft_count', 'sum'),
        hard_count=('hard_count', 'sum'),
        traditional_count=('traditional_count', 'sum'),
        tall_recommend=('tall_recommend', 'sum'),
        sentiment_count=('sentiment_count', 'sum'))

    # Filter more than 3 ascents per route
    ascent_df9 = ascent_df9[ascent_df9.ascents_count > 3]
    ascent_df9.reset_index(inplace=True)

    # sectors with more than 5 routes
    counts = ascent_df9.sector_id.value_counts()
    ascent_df9 = ascent_df9[~ascent_df9.sector_id.isin(counts[counts < 5].index)]
    ascent_df9.reset_index(inplace=True, drop=True)

    # The routes will be unique, but we only have the route_name as Id 
    # I will asign a route_id to each route based on the name and the crag_id:
    ascent_df10 = ascent_df9.copy()
    ascent_df10.index.names = ['name_id']
    ascent_df10.reset_index(inplace=True)

    # And I will create 2 separate tables, one for identifying the route and the other for the recomendator
    routes_identifier = ascent_df10[['name_id', 'name', 'sector', 'crag', 'country']]
    routes_features = ascent_df10[['name_id', 'name', 'sector_id', 'ascents_count',
                                   'grade_median', 'comment_count', 'rating_mean',
                                   'repeat_count', 'recommend_count', 'chiped_count',
                                   'soft_count', 'hard_count', 'traditional_count',
                                   'sentiment_count', 'tall_recommend']]

    return routes_identifier, routes_features


# ----------------------------- ASCENT TABLE -----------------------------------------------------------------
def clean_ascent(df):
    """
    This function cleans the ASCENT table:

        - Filters the data for outlayers
        - Split notes column
        - Changes route grade by +-1 depending on hard/soft comment
        - Filters naming and sector

    input:
    df -> ascen table

    output:
    ascent_clean

    """

    # Filter
    ascent_df2 = df.copy()
    ascent_df2 = ascent_df2[ascent_df2.exclude_from_ranking == 0]
    ascent_df2 = ascent_df2[ascent_df2.climb_type == 0]  # sportsclimb
    ascent_df2 = ascent_df2.drop(
        columns=['raw_notes', 'exclude_from_ranking', 'climb_type', 'total_score', 'date', 'year', 'rec_date',
                 'project_ascent_date', 'yellow_id', 'climb_try', 'description', 'method_id', 'last_year'])
    print("2..", ascent_df2.shape)

    # Split notes column
    ascent_df3 = ascent_df2.copy()
    ascent_df3.notes = ascent_df3.notes.fillna('-')
    ascent_df3.reset_index(drop=True, inplace=True)
    notes = ascent_df3.notes.apply(clean_jor.Split_notes)
    notes_df = pd.DataFrame(notes.to_list(), columns=['first_ascent', 'soft', 'hard', 'traditional'])
    ascent_df3 = pd.concat([ascent_df3, notes_df], axis=1)
    ascent_df3 = ascent_df3.drop(columns=['notes'])

    # Applly +-1 grade to an easy/hard route
    ascent_df3.grade_id = ascent_df3.apply(clean_jor.Easy_hard, axis=1)

    # all to lowercase
    ascent_df3['name'] = ascent_df3.name.apply(lambda x: str(x).lower())
    ascent_df3['crag'] = ascent_df3.crag.apply(lambda x: str(x).lower())
    ascent_df3['country'] = ascent_df3.country.apply(lambda x: str(x).lower())
    ascent_df3['comment'] = ascent_df3.comment.apply(lambda x: str(x).lower())
    ascent_df3['sector'] = ascent_df3.sector.apply(lambda x: str(x).lower())
    ascent_df3['comment_bool'] = ascent_df3.comment.apply(lambda x: 0 if len(x) < 3 else 1)
    print("3..", ascent_df3.shape)

    # Grade below 9c
    ascent_df4 = ascent_df3.copy()
    ascent_df4 = ascent_df4[ascent_df4['grade_id'] < 79]  # below 9c
    ascent_df4 = ascent_df4[ascent_df4['grade_id'] > 28]  # # above 5a
    ascent_df4.comment = ascent_df4.comment.fillna('-')
    ascent_df4.dropna(subset=['name'], inplace=True)
    ascent_df4.reset_index(drop=True, inplace=True)
    print("4..", ascent_df4.shape)

    # Filter the weird Naming
    ascent_df5 = ascent_df4.copy()
    ascent_df5 = ascent_df5["?" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["??" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["don't know name" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["???" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["¿?" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["unknown" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["no name" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["????" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["?????" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["??????" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["? no name" != ascent_df5["name"]]
    ascent_df5 = ascent_df5["senza nome" != ascent_df5["name"]]
    print("5..", ascent_df5.shape)

    # filter no crag no sector
    ascent_df5 = ascent_df5[ascent_df5.crag_id != 0]
    ascent_df5 = ascent_df5[ascent_df5.sector_id != 0]
    ascent_df5.reset_index(drop=True, inplace=True)
    print("6..", ascent_df5.shape)

    ascent_df5['sentiment'] = ascent_df5.sentiment.apply(lambda x: 0 if x == 'err' else float(x))
    print("7..", ascent_df5.shape)

    return ascent_df5
