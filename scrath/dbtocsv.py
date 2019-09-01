import sqlite3 as sql
import pandas as pd 
import configparser
import os

configfile="./scratch.ini"
conf=configparser.ConfigParser()

if os.path.exists(configfile):
    conf.read(configfile)
else:
    print("no ini file")
    quit
    

dbfile=conf.get("setting","dbfile")
outfile=os.path.splitext(dbfile)[0]+".csv"

conn=sql.connect(dbfile)
df=pd.read_sql_query("SELECT * FROM data",conn)
conn.close()
df.to_csv(outfile)
