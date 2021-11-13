import os, json

from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

import requests

from helpers import login_required


app = Flask(__name__)

# Check for environment variable
if not ("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://fwlfbjnnjqecrd:bff7c450d7cb672504b950a6458c0deb08a7cc59e7d153ed1e50e360d91ea08e@ec2-18-214-238-28.compute-1.amazonaws.com:5432/d5m5ucfcvpvhke")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    username = request.form.get("username")


    if request.method == "POST":

        
        if not request.form.get("username"):
            flash("debes ingresar el nombre del usuario")
            return render_template("login.html")
           

        
        elif not request.form.get("password"):
            flash("debes ingresar la contraseña")
            return render_template("login.html")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        
        result = rows.fetchone()

        if result == None or not check_password_hash(result[2], request.form.get("password")):
            flash("contraseña incorrecta")
            return render_template("login.html")

        session["user_id"] = result[0]
        

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if  request.method == "POST":
        if not request.form.get("username"):
            flash("Debe ingresar el nombre de usuario")
            return render_template("register.html")

        if db.execute("SELECT * FROM users WHERE username = :username",
            {"username":request.form.get("username")}).fetchone():
            flash("el nombre de usuario ya existe")
            return render_template("register.html")

        if not request.form.get("password"):
            flash("debe proporcionar contraseña :v ")
            return render_template("register.html")
        
        if request.form.get("password")!= request.form.get("confirmation"):
            flash("las contraseñas no son las mismas :c")
            return render_template("register.html")
        
        if not request.form.get("confirmation"):
            flash("debe confirmar la contraseña :c")
            return render_template("register.html")

        hash = generate_password_hash(request.form.get("password"))
       
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
            {"username":request.form.get("username"),"password":hash})

        db.commit()

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
def logout(): 

    session.clear()

    return redirect("/")

@app.route("/search", methods=["GET"])
@login_required
def search():

 
    if not request.args.get("book"):
        flash(" debes proporcionar un dato del libro :c")
        return render_template("results.html")

   
    query = "%" + request.args.get("book") + "%"

  
    query = query.title()
    
    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :query OR \
                        title LIKE :query OR \
                        author LIKE :query LIMIT 15",
                        {"query": query})
    

    if rows.rowcount == 0:
        flash(" no podemos encontrar libros con descripcion bro :c")
        return render_template("results.html")  
    

    books = rows.fetchall()

    return render_template("results.html", books=books)

@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):

 if  request.method == "POST":

     informacion = session["user_id"]

     # en este espacio calificacion y comentario.

     calificacion = request.form.get("rating")
      
     comentarios   = request.form.get("comentario")

     row = db.execute( "select id from books where isbn = :isbn",{"isbn": isbn})

     book_id = row.fetchone()[0]
     
     db.execute ( " insert INTO reseñas (user_id,book_id,comentarios,calificacion)  VALUES  (:user_id , :book_id , :comentarios , :calificacion)", 
    {
      "user_id"  : session["user_id"],
      "book_id"    :book_id ,
      "comentarios" :comentarios,
      "calificacion":calificacion,
    })
     db.commit()

     flash(" reseña enviada ")

     return redirect("/book/" + isbn)
 else:
    row = db.execute( "select id from books where isbn = :isbn",{"isbn": isbn})

    book_id = row.fetchone()[0]
    yaComentado = db.execute("select * from reseñas where book_id = :book_id and user_id = :user_id",{'book_id': book_id, 'user_id': session['user_id'] }).fetchone()
    
    row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                        {"isbn": isbn})

    infolibro= row.fetchall()

       
    query = requests.get("https://www.goodreads.com/book/review_counts.json",params={"isbns": isbn})

        
    response = query.json()

        
    response = response['books'][0]

    infolibro.append(response)

        
    row = db.execute("select id FROM books WHERE isbn = :isbn", {"isbn": isbn})

    book = row.fetchone() 
    book = book[0]

      
    results = db.execute(f"select * FROM reseñas r INNER JOIN users u on r.user_id = u.id inner join books b on  r.booK_id = b.id where r.book_id = {book}")

    reviews = results.fetchall()

    return render_template("book.html", infolibro=infolibro, reviews=reviews, yaComentado = yaComentado)
     
@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):

    

    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(relacion.id) as review_count, \
                    AVG(relacion.calificacion) as average_score \
                    FROM books \
                    INNER JOIN relacion \
                    ON books.id = relacion.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn})

   
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    
    tmp = row.fetchone()

  
    result = dict(tmp.items())

   
    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)







  