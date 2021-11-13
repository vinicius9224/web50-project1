import os,json

from helpers import login_required
from flask import Flask, session ,request, redirect, render_template,flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

import requests


# Set up database
engine = create_engine("postgresql://fwlfbjnnjqecrd:bff7c450d7cb672504b950a6458c0deb08a7cc59e7d153ed1e50e360d91ea08e@ec2-18-214-238-28.compute-1.amazonaws.com:5432/d5m5ucfcvpvhke")
db = scoped_session(sessionmaker(bind=engine))


db.execute("create table users (id serial PRIMARY KEY NOT NULL , username VARCHAR NOT NULL , hash VARCHAR NOT NULL )")

db.execute("create table books (id serial PRIMARY KEY NOT NULL , isbn VARCHAR NOT NULL , title VARCHAR NOT NULL ,author VARCHAR NOT NULL , year VARCHAR NOT NULL )")

db.execute ("create table reseñas (id serial PRIMARY KEY NOT NULL, comentarios VARCHAR , calificacion  integer , user_id integer references users, book_id integer references books )")



db.commit()







