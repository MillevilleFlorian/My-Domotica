from os import stat
from mysql.connector.cursor import SQL_COMMENT
from mysql.connector.errors import DatabaseError
from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_status_temp():
        sql = "SELECT waarde FROM project_one.meting where componentid = 2 order by metingid desc limit 1"
        return Database.get_one_row(sql)

    @staticmethod
    def add_meting_temp(waarde):
        sql = "insert into project_one.meting(waarde,componentid) values(%s,2)"
        params = [waarde]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_meting_beweging(waarde):
        sql = "insert into project_one.meting(waarde,componentid) values(%s,1)"
        params = [waarde]
        return Database.execute_sql(sql,params)
    
    @staticmethod 
    def add_meting_rook(waarde):
        sql = "insert into project_one.meting(waarde,componentid) values(%s,6)"
        params = [waarde]
        return Database.execute_sql(sql,params)
    
    @staticmethod
    def add_stand_vent(waarde):
        sql = 'insert into project_one.meting(waarde,componentid) values(%s,4)'
        params = [waarde]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_stand_buzzer(waarde):
        sql = 'insert into project_one.meting(waarde,componentid) values(%s,5)'
        params = [waarde]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_stand_lamp(waarde):
        sql = 'insert into project_one.meting(waarde,componentid) values(%s,3)'
        params = [waarde]
        return Database.execute_sql(sql,params)

    @staticmethod
    def delete_data_beweging():
        sql = "delete from project_one.meting where componentid = 1"
        return Database.execute_sql(sql)

    @staticmethod 
    def delete_data_temp():
        sql = "delete from project_one.meting where componentid = 2"
        return Database.execute_sql(sql)

    @staticmethod
    def reset_AI():
        sql = "ALTER TABLE meting AUTO_INCREMENT=0"
        return Database.execute_sql(sql)
