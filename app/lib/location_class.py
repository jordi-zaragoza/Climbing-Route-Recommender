class Location:

    def __init__(self, routes):
        print("Location class initialized")
        self.routes = routes

    # -------------- Routes df handling ------------------------

    def remove_route(self, name_id):
        """
        This method removes the route with the id name_id from the routes df
        """
        self.routes = self.routes[self.routes.name_id != name_id]
        print("Route removed, name_id -> ", name_id)

    # -------------- Lists of names -----------------------------

    def all_countries(self):
        """
        It returns a list of countries
        """
        return self.routes.country.unique()

    def crags_in_country(self, country):
        """
        It returns the crags list inside a country
        """
        df = self.routes[self.routes.country == country]
        return df.crag.unique()

    def sectors_in_crag(self, crag):
        """
        It returns the crags list inside a country
        """
        df = self.routes[self.routes.crag == crag]
        if len(df.country.unique()) > 1:
            print("same crag: ", crag, "in different countries: ", df.country.unique())
        return df.sector.unique()

    # -------------- Dataframes -----------------------------

    def routes_in_country(self, country):
        return self.routes[self.routes.country == country]

    def routes_in_crag(self, country, crag):
        routes_f = self.routes_in_country(country)
        return routes_f[routes_f.crag == crag]

    def routes_in_sector(self, country, crag, sector):
        routes_f = self.routes_in_crag(country, crag)
        return routes_f[routes_f.sector == sector]
