import sqlite3 as sql 

class miyadb:
    dbname=""
    db=None
    cr=None
    key=None
    tablename=None
    def __init__(self,name,keylist):
        self.dbname=name
        self.db=sql.connect(name)
        self.cr=self.db.cursor()
        self.key=keylist
    def init_table(self):
        
        try:
            create_table = '''CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, time text,temp real, humid real,ave real,std real,numdata int,rawdata text)'''
            #create_table=sql
            self.cr.execute(create_table)
            
        except:
            pass
#            drop_table='''drop table users'''
#            self.cr.execute(drop_table)
#            create_table = '''create table data (id int, time varchar(64),
#                     temp real, humid real,ave real,std real)'''
#            self.cr.execute(create_table)

        self.db.commit()
    
    def init_table2(self):
        sqltemp=""
        try:
            sqltemp=",".join([kk+" "+val for kk,val in self.key])
            
            sql="CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY,"+sqltemp+")"
            #create_table = '''create table data (id int, time text,temp real, humid real,ave real,std real,numdata int,rawdata text)'''
            create_table=sql
            self.cr.execute(create_table)
            
        except:
            print("create table error")
            pass
#            drop_table='''drop table users'''
#            self.cr.execute(drop_table)
#            create_table = '''create table data (id int, time varchar(64),
#                     temp real, humid real,ave real,std real)'''
#            self.cr.execute(create_table)

        self.db.commit()
    
    
    
    def append(self,dat):
        sql = 'insert into data (id, time ,temp,humid,ave,std,numdata,rawdata) values (?,?,?,?,?,?,?,?)'
#        print(dat)
        inp = (dat[0],dat[1],dat[2],dat[3],dat[4],dat[5] ,dat[6],dat[7])
        print(inp)
        self.cr.execute(sql, inp)
        self.db.commit()
    def append2(self,inp):
        sqltemp=",".join([kk for kk,val in self.key])
        valtemp=",".join("?" for t in range(len(self.key)))
        sql="insert into data({0}) values({1})".format(sqltemp,valtemp)
        print(inp)
#        inp = (dat[0],dat[1],dat[2],dat[3],dat[4],dat[5] ,dat[6],dat[7])
        self.cr.execute(sql, inp)
        self.db.commit()

    def remake(self):
        drop_table='''drop table data'''
        self.cr.execute(drop_table)
        create_table = '''create table data (id int, time text,temp real, humid real,ave real,std real,numdata int,rawdata text)'''
        self.cr.execute(create_table)
        self.db.commit()
        

    def clear(self):
        drop_table='''drop table if exists data'''
        self.cr.execute(drop_table)
        self.db.commit()