from flask import Flask, abort, render_template, request, redirect, url_for, jsonify
from math import ceil
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, select, Identity, ForeignKey, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import timedelta
from flask import session #A Flask session can persist between visits if the browser still has the session cookie and it has not expired. (A session in Flask is a way to remember information about one specific user across multiple requests.)
import datetime
import random


# for the secret key holding
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into environment

app = Flask(__name__)
# Now you can access variables like this:
# app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
#same as app.secret_key = string

app.permanent_session_lifetime = timedelta(days=7)# It enables session persistence beyond closing the browser, with a default lifespan of 31 days. If inactive, the session cookie expires, forcing user re-authentication.

conn_temp = create_engine(os.getenv("SQL_URL")) # This connects to MySQL server only without opening a database

with conn_temp.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS BANKDB"))
    conn.commit()

conn_str = os.getenv("DB_URL")
engine = create_engine(conn_str, echo=True)

class Base(DeclarativeBase):
    pass

# This will require changes
class User(Base): # this is using the Base class that originates from the DeclarativeBase that is used to create the format of a table 
    __tablename__ = "users" # this is the name of the table 
    userID:    Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True, autoincrement=True) #  refers to the SQL Server IDENTITY syntax, where the two integers represent the seed (starting value) and the increment (step value).
    firstName:  Mapped[str] = mapped_column(String(50), nullable=True)
    lastName:  Mapped[str] = mapped_column(String(50), nullable=True)
    ssn: Mapped[str] = mapped_column(String(11), unique=True, nullable=True)
    phoneNumber: Mapped[str] = mapped_column(String(20),unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(75), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True)
    isVerified: Mapped[bool] = mapped_column(default=False)
    isAdmin: Mapped[bool] = mapped_column(default=False)

Base.metadata.create_all(engine)

with Session(engine) as event:
    exists = event.scalars(select(User).where(User.email == "admin@tsct.com")).first()
    
    if not exists:
        event.add(User(firstName='Admin', username="admin", email="admin@tsct.com", password=os.getenv("ADMINPW"), isVerified=1, isAdmin=1))
        event.commit()
        
@app.route('/')
def index():
    return render_template('index.html', session=session)
