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
from datetime import date


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
            today = date.today().strftime("%Y-%m-%d")
            values = sql_manager.load_update_values(today)
            remain_cal = round(parameters[0][0] - values[0][0],2)
            return render_template("home.html", user=user, parameters=parameters, values=values, remain_cal=remain_cal)
        else:
            session.pop("email", None)
            session.pop("password", None)
            flash("Wrong email or password", "info")
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

## LOGOUT
@server.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("password", None)
    return redirect(url_for("login"))

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
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    info_values, info_parameters, info_meals = sql_manager.load_journal(email)
    return render_template("nutrition_journal.html", info_values=info_values)

@server.route("/nutrition_info/<key>")
def nutrition_info(key):
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    info_values, info_parameters, info_meals = sql_manager.load_journal(email)
    if (info_meals[key] == []):
        flash("אין ארוחות להיום", "info")
        return render_template("nutrition_info.html",info_values=info_values,info_meals=[])
    else:
        return render_template("nutrition_info.html", info_values=info_values, info_parameters=info_parameters,
                           info_meals=info_meals, key=key)

## DAILY MENU
@server.route("/daily_menu", methods = ['POST', 'GET'], defaults={'mes': None})
@server.route("/daily_menu/<mes>", methods = ['POST', 'GET'])
def daily_menu(mes):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        meals = sql_manager.load_today_menu(1)
        # print(meals)
        if request.method == 'POST':
            meal = request.form["checkMeal"]
            print('m',meal)
            rate = request.form["rate"]
            print('r',rate)
            return redirect(url_for("insert_rate", rate=rate, meal=meal))
        else:
            return render_template("daily_menu.html", meals=meals, mes=mes)

@server.route("/insert_rate/<meal>/<rate>")
def insert_rate(meal,rate):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        mes = sql_manager.insert_rate_to_db(email,meal,rate)
        return redirect(url_for("daily_menu", mes=mes))

## CHANGE MEAL
@server.route("/change_meal")
def change_meal():
    return render_template("change_meal.html")

## PROFILE
@server.route("/my_profile")
def my_profile():
    if "email" not in session:
        return redirect(url_for("login"))
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
@server.route("/update_weight", methods = ['POST', 'GET'])
def update_weight():
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        if request.method == 'POST':
            weight = request.form["weight"]
            print(weight)
            sql_manager.update_wegiht(email, weight)
            return redirect(url_for("my_profile"))
        else:
            return render_template("update_weight.html")




server.run()