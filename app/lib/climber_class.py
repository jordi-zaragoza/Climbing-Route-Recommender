import pandas as pd
from lib import climb_jor, grades_class


class Climber:
    """
    This is the climber (user) class for the route recommender
    """

    climber_count = 0
    num_clusters = 9

    def __init__(self, name=None, grade=54, grade_range=2,
                 location=None,
                 height=170, ascents=0, cluster_init=None):

        if location is None:
            location = ['esp', 'montserrat', 'agulla del senglar']
        print("Climber class initialized")
        self.gr = grades_class.Grades()

        self.routes_liked = pd.DataFrame()
        self.routes_indifferent = pd.DataFrame()
        self.routes_not_liked = pd.DataFrame()

        self.climber_id = self.climber_count

        if name is None:
            self.name = 'climber' + str(self.climber_count)
        else:
            self.name = name

        self.add_climber()

        if isinstance(grade, str):
            self.grade = self.gr.get_grade_id(grade)
        else:
            self.grade = grade

        self.ascents = ascents
        self.location = location  # location = [country,crag,sector]

        self.cluster = [0] * self.num_clusters
        if cluster_init is not None:
            self.cluster[cluster_init] = 1  # it starts giving priority to cluster_init

        self.height = height
        self.grade_range = grade_range

    @classmethod
    def add_climber(cls):
        cls.climber_count = cls.climber_count + 1

    def set_attributes(self, name=None, grade=None, cluster=None, location=None, height=None, grade_range=None,
                       cluster_init=None):
        if name is not None:
            self.name = name
        if grade is not None:
            if isinstance(grade, str):
                self.grade = self.gr.get_grade_id(grade)
            else:
                self.grade = grade
        if cluster is not None:
            self.cluster = cluster
        if location is not None:
            self.location = location  # location = [country,crag,sector]
        if height is not None:
            self.height = height
        if grade_range is not None:
            self.grade_range = grade_range
        if cluster_init is not None:
            self.cluster = [0] * self.num_clusters
            self.cluster[cluster_init] = 1  # it starts giving priority to cluster_init

    # -------------- Route methods ---------------

    def add_cluster(self, cluster_list, like):
        """
        Adds 1 to the cluster of the route liked
        Adds -1 to tho cluster of the route unliked
        """
        for i in range(len(cluster_list)):
            cluster_num = cluster_list.values[i]
            self.cluster[cluster_num] = self.cluster[cluster_num] + like

    def add_route(self, routes):
        if (self.get_routes_climbed().shape[0] == 0) or not (
                routes.name_id.values in self.get_routes_climbed().name_id.values):
            self.ascents = self.ascents + 1
            rt = routes.copy()
            rt['liked'] = 'N/A'
            self.routes_indifferent = pd.concat([self.routes_indifferent, rt])
        else:
            print("Route already in")

    def add_route_liked(self, routes):
        if (self.get_routes_climbed().shape[0] == 0) or not (
                routes.name_id.values in self.get_routes_climbed().name_id.values):
            self.ascents = self.ascents + 1
            rt = routes.copy()
            rt['liked'] = 'Yes'
            self.routes_liked = pd.concat([self.routes_liked, rt])
            self.add_cluster(routes.cluster, 1)
        else:
            print("Route already in")

    def add_route_not_liked(self, routes):
        if (self.get_routes_climbed().shape[0] == 0) or not (
                routes.name_id.values in self.get_routes_climbed().name_id.values):
            self.ascents = self.ascents + 1
            rt = routes.copy()
            rt['liked'] = 'No'
            self.routes_not_liked = pd.concat([self.routes_not_liked, rt])
            self.add_cluster(routes.cluster, -1)
        else:
            print("Route already in")

    def clear_routes(self):
        self.ascents = 0
        self.routes_liked.drop(self.routes_liked.index, inplace=True)
        self.routes_indifferent.drop(self.routes_indifferent.index, inplace=True)
        self.routes_not_liked.drop(self.routes_not_liked.index, inplace=True)
        self.cluster = [0] * self.num_clusters

    # -------------- Get methods ---------------

    def get_data(self):
        return pd.DataFrame({'climber_id': self.climber_id, 'name': self.name, 'ascents': self.ascents,
                             'grade_fra': self.gr.get_fra(self.grade), 'grade': self.grade,
                             'grade_range': self.grade_range, 'country': self.location[0],
                             'crag': self.location[1], 'sector': self.location[2],
                             'height': self.height}, index=[0])

    def get_cluster_order(self):
        # Rearrange this list to see what is the order
        cluster_order = []
        clust_aux = self.cluster.copy()
        for i in range(self.num_clusters):
            max_index = clust_aux.index(max(clust_aux))
            cluster_order.append(max_index)
            clust_aux[max_index] = min(clust_aux) - 1

        return cluster_order

    def get_routes_climbed(self):
        return pd.concat([self.routes_liked, self.routes_indifferent, self.routes_not_liked])

    def get_routes_liked(self):
        return self.routes_liked

    def get_routes_not_liked(self):
        return self.routes_liked
        
    def get_routes_indifferent(self):
        return self.routes_indifferent

    def get_cluster(self):
        return self.cluster
    
    # ---------------- Setter ---------------
    def set_routes_indifferent(self, routes_indifferent):
        self.routes_indifferent = routes_indifferent
        
    def set_routes_liked(self, routes_liked):
        self.routes_liked = routes_liked

    def set_routes_not_liked(self, routes_liked):
        self.routes_liked = routes_liked

    def set_cluster(self, cluster):
        self.cluster = cluster
    
    def set_id(self, climber_id):
        self.climber_id = climber_id
    
    # ---------------- Route recommender ---------- yes here it is ;)

    def recommender_filter(self, df, show=True):
        routes = df.copy()
        # Climber Filters
        routes_tall = climb_jor.filter_tall(routes_df=routes, climber_usr=self, show=show)
        routes_grade = climb_jor.filter_grade(routes_df=routes_tall, climber_usr=self, show=show)

        # Rating Order
        routes_rating = routes_grade.sort_values(by='rating_tot', ascending=False)

        # Clustering Order
        routes_grade = climb_jor.filter_cluster(routes_df=routes_rating, climber_usr=self, show=show)

        return routes_grade

    def route_recommender(self, routes=None, show=False):
        """
        This function returns the route recommendations for the user "climber"
        inputs:
        - climber: the user from the climber class
        - show: True for showing the log

        output:
        df with the recommendations
        """

        if isinstance(routes, type(None)):
            routes = pd.read_csv('../data/routes_rated.csv', low_memory=False, index_col=0)

        # Region
        routes_country = routes[routes.country == self.location[0]]
        routes_crag = routes_country[routes_country.crag == self.location[1]]
        routes_sector = routes_crag[routes_crag.sector == self.location[2]]

        # Recommen
        routes_country_rec = self.recommender_filter(routes_country, show)
        routes_crag_rec = self.recommender_filter(routes_crag, show)
        routes_sector_rec = self.recommender_filter(routes_sector, show)

        if show is True:
            display(routes_country_rec.head(3))
            display(routes_crag_rec.head(3))
            display(routes_sector_rec.head(3))

        return routes_country_rec, routes_crag_rec, routes_sector_rec
