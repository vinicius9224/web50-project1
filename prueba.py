import requests
import os, json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine("postgresql://fwlfbjnnjqecrd:bff7c450d7cb672504b950a6458c0deb08a7cc59e7d153ed1e50e360d91ea08e@ec2-18-214-238-28.compute-1.amazonaws.com:5432/d5m5ucfcvpvhke")
db = scoped_session(sessionmaker(bind=engine))

search = "The Dark Is Rising"

row = db.execute(f"select isbn from books where author='{search}' or isbn='{search}' or title='{search}'").fetchone()[0]

xd = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{row}").json()["items"][0]["volumeInfo"]

print(xd["ratingsCount"])
print(xd["averageRating"])