# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for
from flask import request, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import flask_cors
from flask_cors import CORS
import sql_manager
import json


# Settings
server = Flask(__name__, template_folder='templates')
CORS(server)
server.secret_key = "program"

## WELCOME
@server.route("/welcome", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        session["email"] = email
        password = request.form["password"]
        session["password"] = password
        return redirect(url_for("get_user"))
    else:
        if "email" in session:
            return redirect(url_for("get_user"))
        return render_template("welcome.html")

## SIGN UP - WTF........ OR REGULAR........NOT WORKING.......
@server.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        result = request.form["fname"]
        return redirect(url_for("home", fname=result))
    else:
        return render_template("sign_up.html")

## HOME PAGE
@server.route("/")
def get_user():
    if "email" in session and "password" in session:
        email = session["email"]
        password = session["password"]
        check = sql_manager.check_login_user(email, password)
        if check == True:
            first_name, last_name = sql_manager.load_user(email)
            user = json.dumps(first_name + " " + last_name, ensure_ascii=False).encode('utf8')
            parameters = sql_manager.load_parameters_from_menu(1)
            values = sql_manager.load_update_values()
            remain_cal = round(parameters[0][0] - values[0][0],2)
            return render_template("home.html", user=user, parameters=parameters, values=values,remain_cal=remain_cal)
        else:
            session.pop("email", None)
            session.pop("password", None)
            flash("Wrong email or password", "info")
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@server.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("password", None)
    return redirect(url_for("login"))

## DAILY MENU
@server.route("/daily_menu")
def daily_menu():
    return render_template("daily_menu.html")

## CHANGE MEAL
@server.route("/change_meal")
def change_meal():
    return render_template("change_meal.html")

## SEARCH
@server.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        print("check")
        search_value = request.form["item"]
        if search_value != "":
            ingredients = sql_manager.load_ingredient(search_value)
            dishes = sql_manager.load_dish(search_value)
            meals = sql_manager.load_meal(search_value)
            print(ingredients, dishes, meals)
            if (ingredients == False) and (dishes == False) and (meals== False):
                flash("ערך לא קיים", "info")
                return render_template("search.html")
            else:
                return redirect(url_for("search_result", search_value=search_value))
        else:
            flash("יש להכניס ערך לחיפוש", "info")
            return render_template("search.html")
    else:
        return render_template("search.html")

## SEARCH RESULT
@server.route("/search_result/<search_value>")
def search_result(search_value):
    ingredients = sql_manager.load_ingredient(search_value)
    dishes = sql_manager.load_dish(search_value)
    meals = sql_manager.load_meal(search_value)
    return render_template("search_result.html", search_value=search_value,ingredients=ingredients,dishes=dishes, meals=meals)

## RECIPE
@server.route("/recipe", methods=['POST', 'GET'])
def recipe():
    if request.method == 'POST':
        ingredients = request.form["text"]
        meal_number = request.form["number"]
        print(ingredients)
        # calc the calories:
        return redirect(url_for("recipe_result"))
    else:
        return render_template("recipe.html")

## RECIPE RESULT
@server.route("/recipe_result")
def recipe_result():
    return render_template("recipe_result.html")

## NUTRITION JOURNAL
@server.route("/nutrition_journal")
def nutrition_journal():
    email = session["email"]
    info = sql_manager.load_journal(email)
    print(info)
    return render_template("nutrition_journal.html", info=info)

## PROFILE
@server.route("/my_profile")
def my_profile():
    email = session["email"]
    first_name, last_name, gender, age, height, weight, activity, targ, diet, allergies = sql_manager.load_user_profile(email)
    user = json.dumps(first_name + " " + last_name, ensure_ascii=False).encode('utf8')
    activity = json.dumps(activity, ensure_ascii=False).encode('utf8')
    diet = json.dumps(diet, ensure_ascii=False).encode('utf8')
    s_allergy=""
    for allergy in allergies:
        s_allergy += allergy + ","
    allergy_val = json.dumps(s_allergy, ensure_ascii=False).encode('utf8')
    return render_template('my_profile.html', user=user, age=age, height=height, weight=weight,
                   gender=gender, activity=activity, targ=targ, diet=diet, allergy_val=allergy_val)


## UPDATE WEIGHT
@server.route("/update_weight")
def update_weight():
    return render_template("update_weight.html")






#------------------------------
# Barak Example
@server.route("/getDataFromMyDb", methods=['GET'])
def get_data_from_my_db():
    sql_data = sql_manager.load_data_example()
    dumped_sql_data = json.dumps(sql_data)
    return render_template('show_list.html', title="page",ochel_list=dumped_sql_data)


server.run()