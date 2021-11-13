import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine= create_engine("postgresql://fwlfbjnnjqecrd:bff7c450d7cb672504b950a6458c0deb08a7cc59e7d153ed1e50e360d91ea08e@ec2-18-214-238-28.compute-1.amazonaws.com:5432/d5m5ucfcvpvhke")
db =scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader :
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author , :year)",
                {"isbn": isbn , "title": title , "author": author,"year":year})
    print(f"Added to books {isbn} , {title} , {author} ,{year}")
db.commit()

