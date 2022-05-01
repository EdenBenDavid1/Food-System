# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for
from flask import request, redirect, session, flash
from flask_cors import CORS
import sql_manager, recommendation_algorithm
import json
from datetime import date
from email_validator import validate_email, EmailNotValidError


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
        return redirect(url_for("suggest_algorithm"))
    else:
        if "email" in session:
            return redirect(url_for("suggest_algorithm"))
        return render_template("welcome.html")

## SIGN UP
@server.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        try:
            email = validate_email(email).email
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            mes=str(e)
            return render_template("sign_up.html", mes=mes)
        session["email"] = email
        password = request.form["password"]
        session["password"] = password
        weight = int(request.form["weight"])
        height = int(request.form["height"])
        try:
            check_answer = int(weight)
            assert weight > 25, "הקלד משקל גדול מ25 קילו"
            assert weight < 270, "הקלד משקל קטן מ270 קילו"
        except ValueError:
            mes = 'משקל חייב להיות מספר בקילוגרמים'
        except AssertionError as e:
            mes=str(e)
            return render_template("sign_up.html", mes=mes)
        try:
            check_answer = int(height)
            assert height > 90, "הקלד גובה גדול מ90 ס״מ"
            assert height < 250, "הקלד גובה קטן מ250 ס״מ"
        except ValueError:
            mes = 'גובה חייב להיות מספר בס״מ'
        except AssertionError as e:
            mes=str(e)
            return render_template("sign_up.html", mes=mes)

        gender = request.form["gender"]
        birth_date = request.form["birth_date"]
        diet_id = request.form["diet_id"]
        activity_level = request.form["activity_level"]
        weight_goal = request.form["weight_goal"]
        allergies = request.form.getlist("allergies")
        if allergies == []:
            allergies.append('1') # none allergy
        print(allergies)
        user = sql_manager.create_new_user(fname,lname,email,password,gender,birth_date,height,weight,diet_id,weight_goal,activity_level,allergies)
        if user == True: ## A new user was created
            return redirect(url_for("suggest_algorithm"))
        else: ## the email is already exist
            mes = "המייל קיים, יש לבחור מייל אחר"
            return render_template("sign_up.html",mes=mes)
    else:
        return render_template("sign_up.html",mes=None)

## SEGGEST ALGORITHM:
@server.route("/suggest_algorithm")
def suggest_algorithm():
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        user_id = sql_manager.load_user_id(email)
        user_id_str = str(user_id)
        today = str(date.today())
        print(session)
        if (user_id_str in session) and (today in session[user_id_str][2]):# there is a recommendation for today, for this user
            menu_id = session[user_id_str][1]
            print('already',session)
        else:
            menu_id = recommendation_algorithm.recommendation_algorithm(user_id)
            session[user_id_str] = [user_id_str, menu_id, today]
            list_of_meals = sql_manager.load_today_menu(menu_id)
            list_name = 'meals user ' + user_id_str
            print(list_name)
            session[list_name] = list_of_meals
            print('new',session)
        return redirect(url_for("get_user"))


## HOME PAGE
@server.route("/")
def get_user():
    if "email" in session and "password" in session:
        email = session["email"]
        password = session["password"]
        check = sql_manager.check_login_user(email, password)
        if check == True:
            user_id = sql_manager.load_user_id(email)
            user_id_str = str(user_id)
            # check if the user has a recommendation, if not - go to recommend page
            if user_id_str not in session:
                return redirect(url_for("suggest_algorithm"))
            first_name, last_name = sql_manager.load_user(email)
            user = json.dumps(first_name + " " + last_name, ensure_ascii=False).encode('utf8')
            print(session)
            # load parameters of menu id that was recommended for this user
            menu_id = session[user_id_str][1]
            parameters = sql_manager.load_parameters_from_menu(menu_id)
            today = str(date.today())
            values = sql_manager.load_update_values(today,user_id)
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

## DAILY MENU
@server.route("/daily_menu", methods=['POST', 'GET'], defaults={'new_meal':None,'meal_cal':None,'meal_type':None}) #after relaod the page / after rate
@server.route("/daily_menu/<new_meal>/<meal_cal>/<meal_type>", methods = ['POST', 'GET']) #after change meal
def daily_menu(new_meal,meal_cal,meal_type):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        user_id = str(sql_manager.load_user_id(email))
        list_name = 'meals user ' + str(user_id)
        if request.method == 'POST': #the user press save rate
            meal = request.form["checkMeal"]
            rate = request.form["rate"]
            print(session)
            type = request.form["type"]
            print(type)
            return redirect(url_for("insert_rate", meal=meal, rate=rate, type=type))
        else:
            meal_name_that_eaten = sql_manager.eaten_meals(email)
            print('the new', new_meal, meal_cal)
            # replace the old meal with new one
            if meal_type != None:
                meal_type_dict = {'בוקר': 0, 'צהריים': 1, 'ביניים': 2, 'ערב': 3}
                list_of_meals = session[list_name]
                for meal in list_of_meals:
                    if meal[2] == meal_type:
                        index = meal_type_dict[meal_type]
                        list_of_meals[index] = (new_meal, meal_cal, meal_type)
                        print('the meals', list_of_meals)
                        session[list_name] = list_of_meals
            if meal_type == None:
                list_of_meals = session[list_name]
                print(list_of_meals)
            return render_template("daily_menu.html", list_of_meals=list_of_meals, meal_name_that_eaten=meal_name_that_eaten)

@server.route("/insert_rate/<meal>/<rate>/<type>")
def insert_rate(meal,rate,type):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        mes = sql_manager.insert_rate_to_db(email,meal,rate,type)
        sql_manager.insert_menu_to_history(email)
        return redirect(url_for("daily_menu"))

## CHANGE MEAL
@server.route("/change_meal/<meal_type>/<meal_cal>")
def change_meal(meal_type,meal_cal):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        list_of_suggest_meals = sql_manager.suggest_other_meals(email,meal_cal,meal_type)
        print(list_of_suggest_meals)
        return render_template("change_meal.html", meal_type=meal_type, meal_cal=meal_cal,list_of_suggest_meals=list_of_suggest_meals)

## NUTRITION JOURNAL
@server.route("/nutrition_journal")
def nutrition_journal():
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user_id_str = str(sql_manager.load_user_id(email))
    menu_id = session[user_id_str][1]
    info_values, info_parameters, info_meals = sql_manager.load_journal(email,menu_id)
    return render_template("nutrition_journal.html", info_values=info_values)

@server.route("/nutrition_info/<key>")
def nutrition_info(key):
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    user_id_str = str(sql_manager.load_user_id(email))
    menu_id = session[user_id_str][1]
    info_values, info_parameters, info_meals = sql_manager.load_journal(email,menu_id)
    if (info_meals[key] == []):
        flash("אין ארוחות להיום", "info")
        return render_template("nutrition_info.html",info_values=info_values,info_meals=[])
    else:
        return render_template("nutrition_info.html", info_values=info_values, info_parameters=info_parameters,
                           info_meals=info_meals, key=key)

## PROFILE
@server.route("/my_profile")
def my_profile():
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    first_name, last_name, gender, birth_date, height, weight, activity, targ, diet, allergies = sql_manager.load_user_profile(email)
    birth_date = birth_date.strftime("%d.%m.%Y")
    user = json.dumps(first_name + " " + last_name, ensure_ascii=False).encode('utf8')
    activity = json.dumps(activity, ensure_ascii=False).encode('utf8')
    diet = json.dumps(diet, ensure_ascii=False).encode('utf8')
    s_allergy=""
    for allergy in allergies:
        s_allergy += allergy + ","
    allergy_val = json.dumps(s_allergy, ensure_ascii=False).encode('utf8')
    return render_template('my_profile.html', user=user, birth_date=birth_date, height=height, weight=weight,
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
            # after change a parameter - new recommendation:
            return redirect(url_for("my_profile"))
        else:
            return render_template("update_weight.html")

server.run()