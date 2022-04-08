import pandas as pd
from lib import clean_jor, tables_jor

class grades():
    '''
    This class is used for the grades converter -> grade_fra to grade_id and opposite
    It will load and clean the conversin table on init
    '''
    
    def  __init__(self):
#         print("Grades class initialized")
        aux = tables_jor.conversion_table().drop(columns=['index'])
        self.conversion_table = clean_jor.Correct_conversion_table(aux)
        
    def get_fra(self,grade_id):
        grade_fra = self.conversion_table[self.conversion_table.grade_id == grade_id].grade_fra.values[0]
        return grade_fra
    
    def get_grade_id(self,grade_fra):
        grade_id = self.conversion_table[self.conversion_table.grade_fra == grade_fra].grade_id.values[0]
        return grade_id
    
    def get_grades_fra(self):
        return ['5a', '5b', '5c', '6a', '6a+', '6b', '6b+', '6c', '6c+', '7a', '7a+', '7b', '7b+', '7c',
                '7c+', '8a', '8a+', '8b', '8b+', '8c', '8c+', '9a', '9a+', '9b', '9b+']
    
    def get_grade(self, s):
        if isinstance(s, str):
            return self.get_grade_id(s)
        else:
            return self.get_fra(s)