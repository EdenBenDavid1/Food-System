# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for
from flask import request, redirect, session, flash
import sql_manager, recommendation_algorithm
import json
from datetime import date
from email_validator import validate_email, EmailNotValidError
import ast # cast string to dict

# Settings
server = Flask(__name__, template_folder='templates')
server.secret_key = "program"

## WELCOME
@server.route("/welcome", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        check = sql_manager.check_login_user(email, password)
        # there is no such user with this email and password:
        if check == False:
            flash("אימייל או סיסמא שגויים", "info")
            return render_template("welcome.html")
        else:
            session["email"] = email
            session["password"] = password
            return redirect(url_for("suggest_algorithm"))
    else:
        if "email" in session:
            return redirect(url_for("suggest_algorithm"))
        # the user must login
        return render_template("welcome.html")

## SIGN UP
@server.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        # Get values from form
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        gender = request.form["gender"]
        birth_date = request.form["birth_date"]
        diet_id = request.form["diet_id"]
        activity_level = request.form["activity_level"]
        weight_goal = request.form["weight_goal"]
        allergies = request.form.getlist("allergies")
        password = request.form["password"]
        weight = request.form["weight"]
        height = request.form["height"]

        # Validate values
        validation_errors = []
        # email validate
        try:
            email = validate_email(email).email
        except EmailNotValidError as e:
            # email is not valid
            validation_errors.append(str(e))
        # weight validate
        if weight.isnumeric():
            if int(weight) < 40:
                validation_errors.append("הקלד משקל גדול מ40 קילו")
            if int(weight) > 101:
                validation_errors.append("הקלד משקל קטן מ101 קילו")
        else:
            validation_errors.append("משקל חייב להיות מספר בקילוגרמים")
        # height validate
        if height.isnumeric():
            if int(height) < 90:
                validation_errors.append("הקלד גובה גדול מ90 ס״מ")
            if int(height) > 201:
                validation_errors.append("הקלד גובה קטן מ201 ס״מ")
        else:
            validation_errors.append("גובה חייב להיות מספר בס״מ")
        # if there are errors
        if validation_errors:
            return render_template("sign_up.html", mes=validation_errors)

        # Business Logic
        if allergies == []:
            allergies.append('1')  # none allergy
        user = sql_manager.create_new_user(fname,lname,email,password,gender,birth_date,height,weight,diet_id,
                                           weight_goal,activity_level,allergies)
        # A new user was created
        if user == True:
            session["email"] = email
            session["password"] = password
            return redirect(url_for("suggest_algorithm"))
        # the email is already exist
        else:
            mes = ["המייל קיים, יש לבחור מייל אחר"]
            return render_template("sign_up.html", mes=mes)
    else:
        return render_template("sign_up.html", mes=[])


## SEGGEST ALGORITHM:
@server.route("/suggest_algorithm")
def suggest_algorithm():
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        user_id = sql_manager.load_user_id(email)
        user_id_str = str(user_id)
        print('user_id',user_id_str)
        today = str(date.today())
        print(session)
        session.clear()
        # There is a recommendation for today, for this user
        if (user_id_str in session) and (today in session[user_id_str][2]):
            menu_id = session[user_id_str][1]
            print('already recommended',menu_id,session)
        else:
            menu_id = recommendation_algorithm.recommend_menu_for_user(user_id)
            print(menu_id)
            session[user_id_str] = [user_id_str, menu_id, today]
            list_of_meals = sql_manager.load_meals_from_menu(menu_id)
            meals_of_user = 'meals user ' + user_id_str
            session[meals_of_user] = list_of_meals
            print('new recommend',session)
        return redirect(url_for("get_user"))

## HOME PAGE
@server.route("/")
def get_user():
    if "email" in session and "password" in session:
        email = session["email"]
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
    # when we press search button
    if request.method == 'POST':
        search_value = request.form["item"]
        if search_value != "":
            ingredients = sql_manager.load_ingredient(search_value)
            dishes = sql_manager.load_dish(search_value)
            meals = sql_manager.load_meal(search_value)
            # there isn't any value to this search value in db:
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
    return render_template("search_result.html", search_value=search_value, ingredients=ingredients, dishes=dishes, meals=meals)

## RECIPE
@server.route("/recipe", methods=['POST', 'GET'])
def recipe():
    all_ingredietns = sql_manager.get_all_ingredients()

    # if the user press the button of decipher
    if request.method == 'POST':
        user_ingredients = []
        for index in range(1,11):
            index = str(index)
            ingredient = request.form[index]
            amount = request.form['num'+index]
            # the user chose ingredients:
            if ingredient != '':
                user_ingredients += [(ingredient,amount)]
        print(user_ingredients)
        meals_number = request.form["meals_number"]

        # the user didn't choose ingredients
        if user_ingredients == []:
            flash("יש לבחור ערכים בתיבות", "info")
            return render_template("recipe.html",all_ingredietns=all_ingredietns)

        # the user didn't choose meals number
        elif meals_number == '':
            flash("יש להקליד ערך לכמות המנות הנוצרות בתיבה מטה", "info")
            return render_template("recipe.html", all_ingredietns=all_ingredietns)

        else: # the user chose correct
            meals_number = float(meals_number)
            values = sql_manager.calc_recipe_values(user_ingredients,meals_number)
            ingre_show = sql_manager.show_recipe_ingredients(user_ingredients)
            session['recipe'] = ingre_show
            #print(ingre_show)
            #print(values)
            return redirect(url_for("recipe_result", values=values))
    else:
        return render_template("recipe.html",all_ingredietns=all_ingredietns)

## RECIPE RESULT
@server.route("/recipe_result/<values>")
def recipe_result(values):
    # convert the string to dictionary
    values = ast.literal_eval(values)
    return render_template("recipe_result.html", values=values)

## DAILY MENU
@server.route("/daily_menu", methods=['POST', 'GET'], defaults={'new_meal':None,'meal_cal':None,'meal_type':None}) # after relaod the page / after rate
@server.route("/daily_menu/<new_meal>/<meal_cal>/<meal_type>", methods = ['POST', 'GET']) # after change meal
def daily_menu(new_meal,meal_cal,meal_type):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        user_id = sql_manager.load_user_id(email)
        meals_of_user = 'meals user ' + str(user_id)
        if request.method == 'POST': # the user press save rate
            meal = request.form["checkMeal"]
            rate = request.form["rate"]
            type = request.form["type"]
            print(session)
            return redirect(url_for("insert_rate", meal=meal, rate=rate, type=type))
        else:
            meal_name_that_eaten = sql_manager.eaten_meals(email)
            # replace the old meal with new one, after change meal:
            if new_meal != None:
                print('the new', new_meal, meal_cal)
                # dict that will help to replace the meal in the specific location in list
                meal_type_dict = {'בוקר': 0, 'צהריים': 1, 'ביניים': 2, 'ערב': 3}
                list_of_meals = session[meals_of_user]
                for meal in list_of_meals:
                    if meal[2] == meal_type: # find the type of the replaced meal
                        index_of_meal = meal_type_dict[meal_type]
                        list_of_meals[index_of_meal] = (new_meal, meal_cal, meal_type) # replace this meal with the older
                        print('the meals', list_of_meals)
                        session[meals_of_user] = list_of_meals # update the session
            if new_meal == None: # after reload page
                list_of_meals = session[meals_of_user]
                print(list_of_meals)
            return render_template("daily_menu.html", list_of_meals=list_of_meals, meal_name_that_eaten=meal_name_that_eaten)

@server.route("/insert_rate/<meal>/<rate>/<type>")
def insert_rate(meal,rate,type):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        mes = sql_manager.insert_rate_to_db(email,meal,rate,type)
        print(mes)
        sql_manager.insert_menu_to_history(email)
        return redirect(url_for("daily_menu"))

## CHANGE MEAL
@server.route("/change_meal/<meal_type>/<meal_cal>")
def change_meal(meal_type, meal_cal):
    if "email" not in session:
        return redirect(url_for("login"))
    else:
        email = session["email"]
        dict_of_suggest_meals = sql_manager.suggest_other_meals(email,meal_cal,meal_type)
        #print(dict_of_suggest_meals)
        return render_template("change_meal.html", meal_type=meal_type, meal_cal=meal_cal,dict_of_suggest_meals=dict_of_suggest_meals)

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
            sql_manager.update_weight(email, weight)
            # after change a parameter - new recommendation:
            return redirect(url_for("my_profile"))
        else:
            return render_template("update_weight.html")

server.run()