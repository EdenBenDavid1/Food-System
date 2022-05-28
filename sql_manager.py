import mysql.connector
from datetime import datetime
from datetime import date

# A few function that will help:

# CONNECT TO DB
def connect():
    mydb = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='FoodSystem')
    return mydb

def calc_age(birth_str):
    today = date.today()
    birth_date = datetime.strptime(str(birth_str), '%Y-%m-%d').date()
    year_difference = ((today-birth_date).days)/365
    return round(year_difference,0)
#calc_age('1996-04-25')


## calc user calories base on BMR formula:
def calc_user_calories(gender,birth_date,height,weight,gain_keep_lose,activity_level):
    activity_level_dict = {'ללא אימונים': 1.2, '1-3 אימונים בשבוע': 1.375, '4-5 אימונים בשבוע': 1.55,
                           '6-7 אימונים בשבוע': 1.725, 'עבודה פיזית': 1.9}
    weight_goal_dict = {'להוריד במשקל': 0.8, 'לשמור על המשקל': 1, 'לעלות במשקל': 1.2}
    age = calc_age(birth_date)
    if gender == 'נקבה':
        cal_targ = round((9.247 * float(weight) + 3.098 * float(height) - 4.330 * age + 447.593) * \
                         activity_level_dict[activity_level] * weight_goal_dict[gain_keep_lose], 2)
    else:
        cal_targ = round((13.397 * weight + 4.799 * height - 5.677 * age + 88.362) * \
                         activity_level_dict[activity_level] * weight_goal_dict[gain_keep_lose], 2)
    return cal_targ

#cal = calc_user_calories('נקבה','1996-02-28',153,50,'להוריד במשקל','1-3 אימונים בשבוע')
#print(cal)

def get_user_new_cal_targ(user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT gender,birth_date,height,weight,gain_keep_lose,activity_level FROM foodSystem.users where user_id=%s;"
    mycursor.execute(sql, (user_id,))
    user_parameters = mycursor.fetchall()[0]
    cal_targ = calc_user_calories(user_parameters[0], user_parameters[1], user_parameters[2], user_parameters[3],
                                  user_parameters[4], user_parameters[5])
    return cal_targ

def get_user_cal_targ(user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT cal_targ FROM foodSystem.users where user_id=%s;"
    mycursor.execute(sql, (user_id,))
    user_cal = mycursor.fetchall()[0][0]
    return user_cal

def get_meal_cal(menu_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT menu_cal FROM foodSystem.menus where menu_id=%s;"
    mycursor.execute(sql, (menu_id,))
    menu_cal = mycursor.fetchall()[0][0]
    return menu_cal


def update_user_cal_targ(cal_targ,user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "update foodSystem.users set cal_targ =%s WHERE user_id = %s;"
    val = (cal_targ, user_id)
    mycursor.execute(sql, val)
    mydb.commit()

def get_all_users():
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_id FROM foodSystem.users order by user_id;"
    mycursor.execute(sql1)
    all_users_id = mycursor.fetchall()
    return all_users_id


# calc all users calories
def calc_all_users_calories():
    all_users_id = get_all_users()
    for user in all_users_id:
        cal_targ = get_user_new_cal_targ(user[0])
        update_user_cal_targ(cal_targ,user[0])

#calc_all_users_calories()


# get meal_id from meal_name
def get_meal_id(meal_name):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "select meal_id from meals where meal_name=%s;"
    mycursor.execute(sql1, (meal_name,))
    meal_id = mycursor.fetchall()[0][0]
    return meal_id

## CALC NUTRITION VALUES:
def calc_dishes_table():
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT dish_name, round(SUM(amount*fi_cal),2), round(SUM(amount*fi_carb),2)," \
          "round(SUM(amount*fi_fat),2), round(SUM(amount*fi_protein),2), round(SUM(amount*fi_sugar),2)" \
          "FROM ((foodSystem.food_ingredients fi " \
          "join foodSystem.ingredients_in_dish iid on fi.fi_id=iid.fi_id)" \
          "join foodSystem.dishes d on d.dish_id=iid.dish_id)" \
          "group by dish_name;"
    mycursor.execute(sql1)
    dishes = mycursor.fetchall()
    print(dishes)
    for dish in dishes:
        sql2 = "select dish_id from foodSystem.dishes where dish_name=%s;"
        dish_name = [dish[0]]
        mycursor.execute(sql2, dish_name)
        dish_id = mycursor.fetchall()[0][0]
        sql3 = "UPDATE foodSystem.dishes SET dish_cal =%s, dish_carb=%s, dish_fat=%s, dish_protein=%s, dish_sugar=%s" \
               "WHERE dish_id = %s;"
        val = (dish[1],dish[2],dish[3],dish[4],dish[5],dish_id)
        mycursor.execute(sql3, val)
        mydb.commit()

def calc_meals_table():
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT meal_name, round(sum(dish_cal),2), round(sum(dish_carb),2), round(sum(dish_fat),2), round(sum(dish_protein),2), round(sum(dish_sugar),2)" \
           "FROM ((foodSystem.dishes d " \
           "join foodSystem.dish_in_meal dim on d.dish_id=dim.dishInMeal_dish_id)" \
           "join foodSystem.meals m on m.meal_id=dim.dishInMeal_meal_id)" \
           "group by meal_name;"
    mycursor.execute(sql1)
    meals = mycursor.fetchall()
    print(meals)
    for meal in meals:
        meal_id = get_meal_id(meal[0])
        sql3 = "UPDATE foodSystem.meals SET meal_cal =%s, meal_carb=%s, meal_fat=%s, meal_protein=%s, meal_sugar=%s" \
               "WHERE meal_id = %s;"
        val = (meal[1],meal[2],meal[3],meal[4],meal[5],meal_id)
        mycursor.execute(sql3, val)
        mydb.commit()

def calc_menus_table():
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT menu_name, round(sum(meal_cal),2), round(sum(meal_carb),2), round(sum(meal_fat),2), round(sum(meal_protein),2), round(sum(meal_sugar),2)" \
           "FROM ((foodSystem.meals " \
           "join foodSystem.meals_in_menu mim on meals.meal_id=mim.mealsInMenu_meal_id)" \
           "join foodSystem.menus on menus.menu_id=mim.mealsInMenu_menu_id)" \
           "group by menu_name;"
    mycursor.execute(sql1)
    menus = mycursor.fetchall()
    print(menus)
    for menu in menus:
        sql2 = "select menu_id from foodSystem.menus where menu_name=%s;"
        menu_name = [menu[0]]
        mycursor.execute(sql2, menu_name)
        menu_id = mycursor.fetchall()[0][0]
        sql3 = "UPDATE foodSystem.menus SET menu_cal =%s, menu_carb=%s, menu_fat=%s, menu_protein=%s, menu_sugar=%s" \
               "WHERE menu_id = %s;"
        val = (menu[1],menu[2],menu[3],menu[4],menu[5],menu_id)
        mycursor.execute(sql3, val)
        mydb.commit()

#calc_dishes_table()
#calc_meals_table()
#calc_menus_table()

## WELCOME
# Check if email and password exist and true
def check_login_user(email,password):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT email, password FROM FoodSystem.users WHERE email=%s and password=%s;"
    user = (email,password)
    mycursor.execute(sql, user)
    result = mycursor.fetchall()
    # if result is empty (not found) return False:
    if result == []:
        return False
    else:
        return True

#s = check_if_email_exist('liri_viyner@gmail.com')
#print(s)

## SIGN_UP:
def check_if_email_exist(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT email FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql, (email,))
    result = mycursor.fetchall()
    # if result is empty (not found) return False:
    if result == []:
        return False
    else:
        return True

# create new user in db
def create_new_user(user_fname,user_lname,email,password,gender,birth_date,height,weight,diet_id,gain_keep_lose,activity_level,allergies):
    mydb = connect()
    mycursor = mydb.cursor()
    # check if the email exist - so the user is already exist.
    email_exist = check_if_email_exist(email)
    if email_exist == True:
        return False
    else: # Add new user:
        # calc cal_targ:
        cal_targ = calc_user_calories(gender,birth_date,height,weight,gain_keep_lose,activity_level)
        sql1 = "SELECT user_id FROM foodSystem.users ORDER BY user_id DESC LIMIT 1;"  # get the last user number
        mycursor.execute(sql1)
        last_user_id = mycursor.fetchall()[0][0]
        new_user_id = last_user_id + 1
        sql2 = "INSERT INTO foodSystem.users (user_id,user_fname,user_lname,email,password,gender,birth_date,height,weight,diet_id," \
              "gain_keep_lose,activity_level,cal_targ) " \
              "values (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        val = (new_user_id,user_fname,user_lname,email,password,gender,birth_date,height,weight,diet_id,gain_keep_lose,activity_level,cal_targ)
        mycursor.execute(sql2, val)
        mydb.commit()
        for allergy in allergies:
            print(allergy)
            sql2 = "insert into foodSystem.user_allergies(user_id, allergy_id) values(%s, %s);"
            val2 = (new_user_id, allergy)
            mycursor.execute(sql2, val2)
            mydb.commit()
        return True

#user = create_new_user('עדן', 'בן דוד', 'eden2802@gmail.com', '444','נקבה','1996-02-28',153,50,1,'להוריד במשקל','1-3 אימונים בשבוע')
#print(user)

## HOME:
# load full name to first page:
def load_user(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT user_fname, user_lname, email FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql, (email,))
    result = mycursor.fetchall()
    return result[0][0], result[0][1]

# After the algorithm suggest a daily menu, show the menu values:
def load_parameters_from_menu(menu):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT round(menu_cal,2),round(menu_carb,2),round(menu_protein,2),round(menu_fat,2) " \
          "FROM foodSystem.menus WHERE menu_id=%s;"
    mycursor.execute(sql, (menu,))
    result = mycursor.fetchall()
    return result

#parameters = load_parameters_from_menu(1)
#print(parameters)
#for para in parameters:
#    print(para)

# return the user_id to an email
def load_user_id(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_id FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql1, (email,))
    user_id = mycursor.fetchall()[0][0]
    return user_id

# After the algorithm suggest a daily menu, show the update values, according to what the user ate:
def load_update_values(date,user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "select round(sum(meal_cal),2),round(sum(meal_carb),2),round(sum(meal_protein),2),round(sum(meal_fat),2) " \
          "from foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id where date=%s and rates_user_id=%s;"
    mycursor.execute(sql,(date,user_id))
    result = mycursor.fetchall()
    # id the user didn't eat anything yet:
    if result == [(None, None, None, None)]:
        result = [(0,0,0,0)]
    return result

#values = load_update_values('2022-05-11',2)
#for val in values:
#    print(val)

## DAILY MENU
def load_today_menu(menu):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT ml.meal_name,ml.meal_cal,mt.type_name " \
          "FROM (((foodSystem.menus as mn " \
          "join foodSystem.meals_in_menu as mim on mn.menu_id=mim.mealsInMenu_menu_id)" \
          "join foodSystem.meals as ml on ml.meal_id=mim.mealsInMenu_meal_id)" \
          "join foodSystem.meal_type as mt on mim.mealsInMenu_meal_type_id=mt.type_id)" \
          "where menu_id=%s " \
          "order by mealsInMenu_meal_type_id;"
    mycursor.execute(sql, (menu,))
    result = mycursor.fetchall()
    return result

#l = load_today_menu(2)
#print(l)

# after the user ate meal, he can't check "ate" again and can't change this meal:
def eaten_meals(email):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    sql = "SELECT meal_name FROM (foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id)" \
           "where rates_user_id=%s and date=current_date();"
    mycursor.execute(sql, (user_id,))
    result = mycursor.fetchall()
    meals_name = []
    for meal in result:
        meals_name.append(meal[0])
    #print(meals_name)
    if meals_name == []: #there is no rates for today
        return []
    else:
        return meals_name

def insert_rate_to_db(email,meal_name,rate,type):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    meal_id = get_meal_id(meal_name)
    sql1 = "SELECT rates_user_id, rates_meal_id, rate, date FROM foodSystem.rates " \
           "where rates_user_id=%s and rates_meal_id=%s and date=current_date();"
    val2 = (user_id, meal_id)
    mycursor.execute(sql1, val2)
    exist = mycursor.fetchall()
    if exist == []: # there is no such row:
        sql2 = "INSERT INTO foodSystem.rates (rates_user_id,rates_meal_id,meal_type, rate, date) VALUES (%s, %s, %s,%s, current_date());"
        val2 = (user_id, meal_id,type, rate)
        mycursor.execute(sql2, val2)
        mydb.commit()
        return "דירוג נשמר"
    else:
        if (int(rate) == (exist[0][2])):
            return "כבר דירגת ארוחה זו"
        else:
            return "קיים דירוג אחר עבור ארוחה זו"

#rate = insert_rate_to_db('roni_zarfati@gmail.com','יוגורט עם דבש',4)
#print(rate)
#insert_rate_to_db()
#now = datetime.now()
#current_time = now.strftime("%H:%M:%S")
#print(current_time)

def create_new_menu_in_db():
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT menu_id FROM foodSystem.menus ORDER BY menu_id DESC LIMIT 1;" # get the last menu number
    mycursor.execute(sql1)
    last_menu_id = mycursor.fetchall()[0][0]
    new_menu_id = last_menu_id + 1
    sql2 = "insert into foodSystem.menus (menu_id,menu_name) VALUES (%s,%s);"  # create a new menu
    new_menu_name = ('תפריט מספר' + ' ' + str(new_menu_id))
    mycursor.execute(sql2, (new_menu_id,new_menu_name))
    mydb.commit()
    return new_menu_id


def get_diet_for_user(user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT diet_id FROM foodSystem.users where user_id=%s;"
    mycursor.execute(sql1, (user_id,))
    diet_id = mycursor.fetchall()[0][0]
    return diet_id

def insert_into_menu_history(user_id, menu, avg_rate,menu_exist):
    mydb = connect()
    mycursor = mydb.cursor()
    diet_id = get_diet_for_user(user_id)
    sql1 = "insert into foodSystem.menu_history (history_user_id,history_menu_id,date,avg_rate)" \
           "VALUES (%s,%s,current_date(),%s);"
    val1 = (user_id, menu, avg_rate)
    mycursor.execute(sql1, val1)
    mydb.commit()
    if menu_exist == False: # this is a new menu, and we need to add it to the diet_for_menu table
        sql2 = "insert into foodSystem.diet_for_menu(dietMenu_menu_id, dietMenu_diet_id) values(%s,%s);"
        val2 = (menu,diet_id)
        mycursor.execute(sql2, val2)
        mydb.commit()


# insert menu to history table:
def insert_menu_to_history(email):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    # check if there are 4 meals today for this user:
    sql1 = "SELECT rates_meal_id,meal_type, rate FROM foodSystem.rates where rates_user_id=%s and date=current_date()" \
           "order by meal_type;"
    mycursor.execute(sql1, (user_id,))
    meals = mycursor.fetchall()
    print(meals)
    if len(meals) == 4:
        avg_rate = (meals[0][2] + meals[1][2] + meals[2][2] + meals[3][2]) / 4
        # check if there is a menu from this 4 meals:
        sql2 = "SELECT mealsInMenu_menu_id, count(*) count " \
               "FROM (foodSystem.meals_in_menu)" \
               "WHERE (mealsInMenu_meal_id IN (%s,%s,%s,%s))" \
               "GROUP BY (mealsInMenu_menu_id);"
        val = (meals[0][0], meals[1][0], meals[2][0], meals[3][0])
        mycursor.execute(sql2, val)
        menus = mycursor.fetchall()
        print(menus)
        menu_exist = False
        for menu in menus:
            if menu[1] == 4: # there is a menu with the 4 meals that eaten
                menu_exist = True
                insert_into_menu_history(user_id,menu[0],avg_rate,menu_exist)
                print("תפריט רגיל נכנס להיסטוריה")
        if menu_exist == False: # there isn't exist menu with this 4 meals
            new_menu_id = create_new_menu_in_db()
            for meals_in_menu in meals: # insert meals in menu
                sql3 = "insert into foodSystem.meals_in_menu (mealsInMenu_menu_id,mealsInMenu_meal_id,mealsInMenu_meal_type_id) " \
                "VALUES (%s,%s,%s);"
                val3 = ((new_menu_id),meals_in_menu[0],meals_in_menu[1])
                mycursor.execute(sql3,val3)
                mydb.commit()
            calc_menus_table() # calc the nutrition values for the new menu
            # insert the new menu to history table
            insert_into_menu_history(user_id, new_menu_id, avg_rate,menu_exist)
            print("תפריט לאחר שינוי נכנס להיסטוריה")
    else:
        print("עוד לא נאכלו 4 ארוחות")

#insert_menu_to_history('may_zemach@gmail.com')


## CHANGE MEAL
def get_user_allergy_ingredients(user_id):
    food_ingredients = []
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT ingreAllergy_fi_id " \
          "FROM foodSystem.user_allergies ua join foodSystem.ingredients_in_allergies iia " \
          "on ua.allergy_id=iia.ingreAllergy_allergy_id " \
          "where user_id=%s;"
    mycursor.execute(sql, (user_id,))
    list_f = mycursor.fetchall()
    for fi_id in list_f:
        food_ingredients.append(fi_id[0])
    return food_ingredients

def get_other_meals_list(diet_id,meal_cal, meal_type):
    list_of_meals = {}
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT distinct(meal_id),meal_name,meal_cal FROM (((foodSystem.diet_for_meal dfm " \
          "join foodSystem.meals m on dfm.mealDiet_meal_id=m.meal_id)" \
          "join foodSystem.meal_classification mc on m.meal_id=mc.mealClass_meal_id)" \
          "join foodSystem.meal_type mt on mc.mealClass_type_id=mt.type_id)" \
          "where (mealDiet_diet_id=%s)" \
          "and (meal_cal between %s-70 and %s+70)" \
          "and (type_name = %s);"
    val = (diet_id, meal_cal, meal_cal, meal_type)
    mycursor.execute(sql, val)
    list_m = mycursor.fetchall()
    print(list_m)
    for meal in list_m:
        list_of_meals[meal[0]] = [meal[1],meal[2]] # create a dictionary, key- meal_id, value- meal_name,meal_cal
    return list_of_meals

def suggest_other_meals(email, meal_cal, meal_type):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    diet_id = get_diet_for_user(user_id)
    food_ingredients_user_cant_eat = get_user_allergy_ingredients(user_id)
    list_of_meals = get_other_meals_list(diet_id,meal_cal, meal_type)
    # check if user can eat the meal, regards to allergies:
    for meal_id in list(list_of_meals): # to avoid dictionary changed size during iteration
        sql = "select distinct(fi_id) " \
               "from foodSystem.dish_in_meal dim join foodSystem.ingredients_in_dish iid on dim.dishInMeal_dish_id = iid.dish_id " \
               "where dishInMeal_meal_id = %s;"
        mycursor.execute(sql, (meal_id,))
        food_id_from_meal = mycursor.fetchall() # list of ingredients that combine this meal
        for food_id in food_id_from_meal:
            if food_id[0] in food_ingredients_user_cant_eat:
                list_of_meals.pop(meal_id)
                break

    return list_of_meals

#f = suggest_other_meals('ariel_cohen@gmail.com',350,'בוקר')
#print(f)

## NUTRITION JOURNAL
# load the meals the user ate today
def load_rated_meals(date,user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "select meal_name, meal_cal,meal_type from foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id " \
          "where date=%s and r.rates_user_id=%s " \
          "order by meal_type;"
    mycursor.execute(sql,(date,user_id))
    result = mycursor.fetchall()
    # id the user didn't eat anything yet:
    if result == []:
        return []
    else:
        return result

#f = load_rated_meals('2022-04-30',1)
#print(f)

# load the journal by an email, and menu
def load_journal(email,menu_id_recommended):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    # load meals history, 7 days back:
    sql1 = "SELECT date, history_menu_id FROM foodSystem.menu_history " \
           "where (date between (current_date()-6) and current_date()) and (history_user_id=%s);"
    mycursor.execute(sql1, (user_id,))
    result = mycursor.fetchall()
    info_values = {}
    info_parameters = {}
    info_meals = {}
    today = date.today()
    # for older dates:
    for history in result:
        h_date = history[0]
        menu = history[1]
        # add to dictionary:
        info_values[h_date.strftime("%d.%m %A")] = load_update_values(h_date,user_id)
        info_parameters[h_date.strftime("%d.%m %A")] = load_parameters_from_menu(menu)
        info_meals[h_date.strftime("%d.%m %A")] = load_today_menu(menu)
    # for today meals and sort by dates:
    info_values[today.strftime("%d.%m %A")] = load_update_values(today,user_id)
    info_values = dict(sorted(info_values.items(), reverse=True, key=lambda item: item[0]))

    info_parameters[today.strftime("%d.%m %A")] = load_parameters_from_menu(menu_id_recommended)
    info_parameters = dict(sorted(info_parameters.items(), reverse=True, key=lambda item: item[0]))

    info_meals[today.strftime("%d.%m %A")] = load_rated_meals(today, user_id)
    info_meals = dict(sorted(info_meals.items(), reverse=True, key=lambda item: item[0]))

    return(info_values, info_parameters, info_meals)

#p = load_journal('roni_zarfati@gmail.com')


## MY_PROFILE
def load_user_basic_info(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_fname, user_lname, gender, birth_date, height, weight, activity_level, cal_targ, diet_id, user_id" \
           " FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql1, (email,))
    basic_info = mycursor.fetchall()[0]
    return basic_info

# load all parameters
def load_user_profile(email):
    mydb = connect()
    mycursor = mydb.cursor()
    basic_info = load_user_basic_info(email)
    sql1 = "SELECT diet_name FROM foodSystem.diets where diet_id=%s;"
    mycursor.execute(sql1, (basic_info[8],))
    diet = mycursor.fetchall()[0][0]
    sql2 = "SELECT allergy_name FROM foodSystem.user_allergies ua join " \
           "foodSystem.allergies_or_sensitivity aos on ua.allergy_id=aos.allergy_id where user_id=%s;"
    mycursor.execute(sql2, (basic_info[9],))
    all_allergies = mycursor.fetchall()
    allergies =[]
    for al in all_allergies:
        allergies.append(al[0])
    return basic_info[0], basic_info[1], basic_info[2], basic_info[3], basic_info[4], basic_info[5],\
           basic_info[6], basic_info[7], diet, allergies

#user=load_user_profile('roni_zarfati@gmail.com')
#print(user)

# change the weight and calculate new calory target
def update_weight(email, weight):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    sql1 = "UPDATE foodSystem.users SET weight = %s WHERE user_id=%s;"
    mycursor.execute(sql1, (weight,user_id))
    mydb.commit()
    cal_targ = get_user_new_cal_targ(user_id)
    update_user_cal_targ(cal_targ, user_id)

#update_weight('roni_zarfati@gmail.com',57)

# RECIPE
def get_all_ingredients():
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT fi_id,fi_name,fi_amount FROM foodSystem.food_ingredients;"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return result

#get_all_ingredients()

def calc_recipe_values(all_ingredients_amout,meals_number):
    mydb = connect()
    mycursor = mydb.cursor()
    nutrition_values = {'קלוריות':0,'פחמימות':0,'שומנים':0,'חלבונים':0}
    # [('3', '1'), ('6', '2')]
    for food_amount in all_ingredients_amout:
        print(food_amount[0])
        fi_id = food_amount[0]
        sql = "SELECT fi_cal,fi_carb,fi_fat,fi_protein FROM foodSystem.food_ingredients " \
          "where fi_id =%s;"
        mycursor.execute(sql,(fi_id,))
        values = mycursor.fetchall() # all values per 1 food ingredient
        print(values)
        for val in values:
            nutrition_values['קלוריות'] += (val[0] * float(food_amount[1]))
            nutrition_values['פחמימות'] += val[1] * float(food_amount[1])
            nutrition_values['שומנים'] += val[2] * float(food_amount[1])
            nutrition_values['חלבונים'] += val[3] * float(food_amount[1])

    for key,value in nutrition_values.items():
        nutrition_values[key] = round(value/meals_number,2)
    return nutrition_values

#calc_recipe_values(all_ingredients_amout,2)

## SEARCH
def load_ingredient(search_value):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT fi_name,fi_amount,fi_cal,fi_carb,fi_fat,fi_protein,fi_sugar" \
          " FROM foodSystem.food_ingredients where fi_name like %s;"
    search_value = ['%' + search_value + ' %']
    mycursor.execute(sql, search_value)
    result = mycursor.fetchall()
    if result == []:
        return False
    return result

#g=load_ingredient('אורז')
#print(g[0])

def load_dish(search_value):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT dish_name,dish_cal,dish_carb,dish_fat,dish_protein FROM foodSystem.dishes where dish_name like %s;"
    search_value = ['%'+search_value+ ' %']
    mycursor.execute(sql, search_value)
    result = mycursor.fetchall()
    if result == []:
        return False
    return result

#ingredient=load_ingredient('דבש')
#for ing in ingredient:
#    print(ing[0])

#dish = load_dish('מבושל')
#for d in dish:
#    print(d[0], d[1])

def load_meal(search_value):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT meal_name,meal_cal,meal_carb,meal_fat,meal_protein FROM foodSystem.meals where meal_name like %s;"
    search_value = ['%' + search_value + ' %']
    mycursor.execute(sql, search_value)
    result = mycursor.fetchall()
    if result == []:
        return False
    return result
