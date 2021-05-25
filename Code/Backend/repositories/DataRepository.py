from mysql.connector.cursor import SQL_COMMENT
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
