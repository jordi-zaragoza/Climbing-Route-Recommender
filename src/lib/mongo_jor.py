import pandas as pd
from lib.climber_class import Climber
from pymongo import MongoClient


def mongo_connect():
    client = MongoClient("mongodb://localhost:27017/")
    mydb = client["recommender"]
    return mydb["climbers"]


def update_climber(climber_dict_new, mycol):
    for climber_dict in list(mycol.find()):
        if climber_dict['climber_id'] == climber_dict_new['climber_id']:
            mycol.update_one(
                climber_dict,
                {"$set": climber_dict_new},
            )
            print("climber successfully updated")


def check_repeated(climber_id, mycol):
    for climber_dict in list(mycol.find()):
        if climber_dict['climber_id'] == climber_id:
            return True

    return False


def save_climber(climber_1):
    mycol = mongo_connect()

    climber_dict = climber_1.get_data().to_dict('records')[0]

    climber_dict['routes_indifferent'] = climber_1.get_routes_indifferent().to_dict('records')
    climber_dict['routes_liked'] = climber_1.get_routes_liked().to_dict('records')
    climber_dict['routes_not_liked'] = climber_1.get_routes_not_liked().to_dict('records')
    climber_dict['clusters'] = climber_1.get_cluster()

    if check_repeated(climber_dict['climber_id'], mycol):
        print("Climber already exists on the database")
        update_climber(climber_dict, mycol)

    else:
        mycol.insert_one(climber_dict)
        print("Created new climber")


def load_climber_dict(climber_id, mycol):
    for climber_dict in list(mycol.find()):
        if climber_dict['climber_id'] == climber_id:
            return climber_dict

    return {}


def load_climber(climber_id):
    mycol = mongo_connect()

    climber_dict = load_climber_dict(climber_id, mycol)

    climber_class = Climber(name=climber_dict['name'],
                            grade=climber_dict['grade'],
                            grade_range=climber_dict['grade_range'],
                            location=[climber_dict['country'], climber_dict['crag'], climber_dict['sector']],
                            height=climber_dict['height'])

    climber_class.set_routes_liked(pd.DataFrame(climber_dict['routes_liked']))
    climber_class.set_routes_not_liked(pd.DataFrame(climber_dict['routes_not_liked']))
    climber_class.set_routes_indifferent(pd.DataFrame(climber_dict['routes_indifferent']))
    climber_class.set_cluster(climber_dict['clusters'])
    climber_class.set_id(climber_dict['climber_id'])

    return climber_class


def list_climbers():
    mycol = mongo_connect()
    climber_names = []
    climber_ids = []
    for climber_dict in list(mycol.find()):
        climber_names.append(climber_dict['name'])
        climber_ids.append(climber_dict['climber_id'])

    return pd.DataFrame({'climber_id': climber_ids, 'name': climber_names})
    
def delete_db():
    mycol = mongo_connect()
    mycol.delete_many({})
