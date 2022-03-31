import pandas as pd

class location():
    
    def __init__(self, routes):
        print("Location class initialized")
        self.routes = routes

        
    def all_countries(self):
        '''
        It returns a list of countries
        '''
        return self.routes.country.unique()


    def crags_in_country(self,country):
        '''
        It returns the crags list inside a country
        '''
        df = self.routes[self.routes.country == country]
        return df.crag.unique()
    
    
    def sectors_in_crag(self,crag):
        '''
        It returns the crags list inside a country
        '''
        df = self.routes[self.routes.crag == crag]
        if (len(df.country.unique()) > 1):
            print("same crag: ", crag,"in different countries: ",df.country.unique)
        return df.sector.unique()