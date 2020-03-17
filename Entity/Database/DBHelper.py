import sqlalchemy
import pandas as pd


class DBHelper:

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.db = "fullfill_db"
        self.engine = None

    def textconnect(self):
        self.__connect__()

    def __connect__(self):
        #constring = "mysql://{0}:{1}@{2}/{3}?charset=utf8".format(self.user, self.password, self.host, self.db)
        constring = "postgres://auzatzkisdsljp:648cbc16f9f7f6a626b6262d4cecac89e23f3462a19d734a94783353a303b0e4@ec2-52-86-33-50.compute-1.amazonaws.com:5432/ddidkg3fq448st"
        self.engine = sqlalchemy.create_engine(constring, pool_recycle=3600)
        self.con = self.engine.connect()
        self.con = self.con.execution_options(
            isolation_level="READ COMMITTED"
        )
        print('connected')
    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql):
        self.__connect__()
        result = self.con.execute(sql)
        self.__disconnect__()
        return result

    def execute(self, sql):
        self.__connect__()
        self.con.execute(sql)
        self.__disconnect__()

    def executetodataframe(self, sql):
        self.__connect__()
        df = pd.read_sql_query(sql, self.engine)
        self.__disconnect__()
        return df

    def executeproc(self, procname):
        self.__connect__()
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc(procname)
        cursor.close()
        connection.commit()
        self.__disconnect__()

    def import_csv_to_db(self, csv_file_path, table):
        with open(csv_file_path, 'r') as file:
            df = pd.read_csv(file)
        self.__connect__()
        df.to_sql(table,
                  con=self.engine,
                  index=False,
                  index_label='sku',
                  if_exists='replace')
        self.__disconnect__()