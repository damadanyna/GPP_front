import pymysql
from sqlalchemy import create_engine

class DB2:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''
        self.database = 'sipem_app'
        self.engine = None
        
    def connect(self):
        if not self.engine:
            self.engine = create_engine(
                f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
            )
        return self.engine
  
