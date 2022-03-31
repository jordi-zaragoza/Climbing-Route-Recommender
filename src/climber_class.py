import pandas as pd
import climb_jor
import grades_class

class climber():
    '''
    This is the climber (user) class for the route recommender    
    '''
    
    climber_count = 0
    num_clusters = 9
     
    def __init__(self, name = None, grade = 54, grade_range = 2,
                 location = ['esp', 'montserrat', 'agulla del senglar'], 
                 height = 170,cluster = [0,0,0,0,0,0,0,0,0]):
        
        print("Climber class initialized")
        self.gr = grades_class.grades()
        
        self.routes_liked = pd.DataFrame()     
        self.routes_indifferent = pd.DataFrame() 
        self.routes_not_liked = pd.DataFrame() 
        
        self.climber_id = self.climber_count 
        
        if name == None:
            self.name = 'climber'+ str(self.climber_count)
        else:
            self.name = name 
        
        self.add_climber()
        
        if isinstance(grade, str):
            self.grade = self.gr.get_grade_id(grade)
        else:
            self.grade = grade      
        
        
        self.location = location # location = [country,crag,sector]
        self.cluster = cluster # its cluster 0 by default
        self.height = height
        self.grade_range = grade_range    
    
    @classmethod    
    def add_climber(cls):
        cls.climber_count = cls.climber_count + 1
                
    def set_attributes(self, name = None, grade = None, cluster = None, location = None, height = None, grade_range = None):
        if name != None:
            self.name = name
        if grade != None:            
            if isinstance(grade, str):
                self.grade = gr.get_grade_id(grade)
            else:
                self.grade = grade  
        if cluster != None:            
            self.cluster = cluster
        if location != None:
            self.location = location # location = [country,crag,sector]
        if height != None:
            self.height = height  
        if grade_range != None:
            self.grade_range = grade_range

# -------------- Route methods ---------------
            
    def add_cluster(self, cluster_list, like):
        '''
        Adds 1 to the cluster of the route liked
        Adds -1 to tho cluster of the route unliked
        '''   
        for i in range(len(cluster_list)):
            cluster_num = cluster_list.values[i]
            self.cluster[cluster_num] = self.cluster[cluster_num] + like    
            
    def add_route(self,routes):
        rt = routes.copy()
        rt['liked'] = 'N/A'
        self.routes_indifferent = pd.concat([self.routes_indifferent, rt])
                
    def add_route_liked(self,routes):
        rt = routes.copy()
        rt['liked'] = 'Yes'
        self.routes_liked = pd.concat([self.routes_liked, rt])
        self.add_cluster(routes.cluster,1)
       
    def add_route_not_liked(self,routes):
        rt = routes.copy()
        rt['liked'] = 'No'
        self.routes_not_liked = pd.concat([self.routes_not_liked, rt])
        self.add_cluster(routes.cluster,-1)
        
    def clear_routes(self):
        self.routes_liked.drop(self.routes_liked.index, inplace=True)
        self.routes_indifferent.drop(self.routes_indifferent.index, inplace=True)
        self.routes_not_liked.drop(self.routes_not_liked.index, inplace=True) 
        self.cluster = [0,0,0,0,0,0,0,0,0]

# -------------- Get methods ---------------        
                
    def get_data(self):
        return pd.DataFrame({'climber_id':self.climber_id,'name':self.name,
                             'grade_fra':self.gr.get_fra(self.grade),'grade':self.grade,
                             'grade_range':self.grade_range,'country':self.location[0],
                             'crag':self.location[1],'sector':self.location[2],
                             'height':self.height}, index=[0])

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
        return pd.concat([self.routes_liked,self.routes_indifferent,self.routes_not_liked])
    
    def get_routes_liked(self):
        return self.routes_liked   
    
    def get_routes_not_liked(self):
        return self.routes_liked 
    
    
# ---------------- Route recommender ---------- yes here it is ;)

    def recommender_filter(self, df, show = True):
        routes = df.copy()
         # Climber Filters    
        routes_tall = climb_jor.filter_tall(routes_df = routes, climber_usr = self, show = show)
        routes_grade = climb_jor.filter_grade(routes_df = routes_tall, climber_usr = self, show = show)

        # Rating Order
        routes_rating = routes_grade.sort_values(by = 'rating_tot',ascending = False)

        # Clustering Order
        routes_grade = climb_jor.filter_cluster(routes_df = routes_rating, climber_usr = self, show = show)

        return routes_grade
        

    def route_recommender(self, show = False):
        '''
        This function returns the route recommendations for the user "climber"
        inputs:
        - climber: the user from the climber class
        - show: True for showing the log

        output:
        df with the recommendations       
        '''


        routes = pd.read_csv('../data/routes_rated.csv',low_memory=False, index_col=0)

        # Region
        routes_country = routes[routes.country == self.location[0]]
        routes_crag = routes_country[routes_country.crag == self.location[1]]
        routes_sector = routes_crag[routes_crag.sector == self.location[2]]

        # Recommen
        routes_country_rec = self.recommender_filter(routes_country, show)
        routes_crag_rec = self.recommender_filter(routes_crag, show)
        routes_sector_rec = self.recommender_filter(routes_sector, show)

        if show == True:
            display(routes_country_rec.head(3))
            display(routes_crag_rec.head(3))
            display(routes_sector_rec.head(3))
            
        return routes_country_rec, routes_crag_rec, routes_sector_rec
       