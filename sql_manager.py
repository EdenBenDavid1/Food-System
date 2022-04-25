import mysql.connector
from datetime import datetime
from datetime import date

# CONNECT TO DB
def connect():
    mydb = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='FoodSystem')
    return mydb

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
        sql2 = "select meal_id from foodSystem.meals where meal_name=%s;"
        meal_name = [meal[0]]
        mycursor.execute(sql2, meal_name)
        meal_id = mycursor.fetchall()[0][0]
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

calc_dishes_table()
calc_meals_table()
calc_menus_table()

email = 'roni_zarfati@gmail.com'


## WELCOME
# Check if email and password are exist and true
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

#s = check_if_email_exist('liri_viyner@gmail.com')
#print(s)

## SIGN_UP:
def create_new_user(user_fname,user_lname,email,password,gender,age,height,weight,diet_id,gain_keep_lose,activity_level):
    activity_level_dict = {'ללא אימונים': 1.2, '1-3 אימונים בשבוע': 1.375, '4-5 אימונים בשבוע': 1.55,
                           '6-7 אימונים בשבוע': 1.725, 'עבודה פיזית': 1.9}
    weight_goal_dict = {'להוריד במשקל': 0.8, 'לשמור על המשקל': 1, 'לעלות במשקל': 1.2}
    mydb = connect()
    mycursor = mydb.cursor()
    # check if the email exist - so the user is already exist.
    email_exist = check_if_email_exist(email)
    if email_exist == True:
        return 'המשתמש קיים במערכת'
    # Add new user:
    else:
        # calc cal_targ:
        if gender == 'נקבה':
            cal_targ = (9.247*weight + 3.098*height - 4.330*age + 447.593) * activity_level_dict[activity_level] *weight_goal_dict[gain_keep_lose]
        else:
            cal_targ = (13.397*weight + 4.799*height - 5.677*age + 88.362) * activity_level_dict[activity_level] *weight_goal_dict[gain_keep_lose]

        sql = "INSERT INTO foodSystem.users (user_fname,user_lname,email,password,gender,age,height,weight,diet_id," \
              "gain_keep_lose,activity_level,cal_targ) " \
              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)";
        val = (user_fname,user_lname,email,password,gender,age,height,weight,diet_id,gain_keep_lose,activity_level,cal_targ)
        mycursor.execute(sql, val)
        mydb.commit()
        return "המשתמש נוצר בהצלחה"

#user = create_new_user('עדן', 'בן דוד', 'eden2802@gmail.com', '444','נקבה',26,153,50,1,'להוריד במשקל','1-3 אימונים בשבוע')
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

# After the algorithm suggest a daily menu, show the menu value:
# Lets say the menu is 1:
def load_parameters_from_menu(menu):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT round(menu_cal,2),round(menu_carb,2),round(menu_protein,2),round(menu_fat,2) " \
          "FROM foodSystem.menus WHERE menu_id=%s;"
    mycursor.execute(sql, (menu,))
    result = mycursor.fetchall()
    return result

#parameters = loat_parameters_from_menu(1)
#print(parameters)
#for para in parameters:
#    print(para)

def load_user_id(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_id FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql1, (email,))
    user_id = mycursor.fetchall()[0][0]
    return user_id


# After the algorithm suggest a daily menu, show the update values, according to what the user ate:
def load_update_values(date):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "select round(sum(meal_cal),2),round(sum(meal_carb),2),round(sum(meal_protein),2),round(sum(meal_fat),2) " \
          "from foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id where date=%s;"
    mycursor.execute(sql,(date,))
    result = mycursor.fetchall()
    # id the user didn't eat anything yet:
    if result == [(None, None, None, None)]:
        result = [(0,0,0,0)]
    return result

#values = load_update_values('2022-04-18')
#for val in values:
#print(values)

## DAILY MENU
def load_today_menu(menu):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT ml.meal_name,ml.meal_cal,mt.type_name " \
          "FROM (((foodSystem.menus as mn " \
          "join foodSystem.meals_in_menu as mim on mn.menu_id=mim.mealsInMenu_menu_id)" \
          "join foodSystem.meals as ml on ml.meal_id=mim.mealsInMenu_meal_id)" \
          "join foodSystem.meal_type as mt on mim.mealsInMenu_meal_type_id=mt.type_id)" \
          "where menu_id=%s;"
    mycursor.execute(sql, (menu,))
    result = mycursor.fetchall()
    return result

#l = load_today_menu(1)
#print(l)

def insert_rate_to_db(email,meal_name,rate):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    sql1 = "select meal_id from meals where meal_name=%s;"
    mycursor.execute(sql1, (meal_name,))
    meal_id = mycursor.fetchall()[0][0]
    sql2 = "SELECT rates_user_id, rates_meal_id, rate, date FROM foodSystem.rates " \
           "where rates_user_id=%s and rates_meal_id=%s and date=current_date();"
    val2 = (user_id, meal_id)
    mycursor.execute(sql2, val2)
    exist = mycursor.fetchall()
    #print(exist)
    # there is no such row:
    if exist == []:
        sql3 = "INSERT INTO foodSystem.rates (rates_user_id, rates_meal_id, rate, date) VALUES (%s, %s, %s, current_date());"
        val3 = (user_id, meal_id, rate)
        mycursor.execute(sql3, val3)
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

## NUTRITION JOURNAL
def load_rated_meals(date,user_id):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "select meal_name, meal_cal from foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id " \
          "where date=%s and r.rates_user_id=%s;;"
    mycursor.execute(sql,(date,user_id))
    result = mycursor.fetchall()
    # id the user didn't eat anything yet:
    if result == []:
        return []
    else:
        return result

f = load_rated_meals('2022-04-20',1)
#print(f)


def load_journal(email):
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
        # add to dictionary and sort:
        info_values[h_date.strftime("%d.%m %A")] = load_update_values(h_date)
        info_values = dict(sorted(info_values.items(), key=lambda item: item[0]))

        info_parameters[h_date.strftime("%d.%m %A")] = load_parameters_from_menu(menu)
        info_parameters = dict(sorted(info_parameters.items(), key=lambda item: item[0]))

        info_meals[h_date.strftime("%d.%m %A")] = load_today_menu(menu)
        info_meals = dict(sorted(info_meals.items(), key=lambda item: item[0]))

    info_values[today.strftime("%d.%m %A")] = load_update_values(today)
    info_parameters[today.strftime("%d.%m %A")] = load_parameters_from_menu(1)
    info_meals[today.strftime("%d.%m %A")] = load_rated_meals(today, user_id)

    return(info_values, info_parameters, info_meals)

#load_journal('roni_zarfati@gmail.com')
#print(sort_info_values)
#print(sort_info_parameters)
#print(sort_info_meals)
#for value in journal['Tuesday 19.04']:
#    print (value)

## MY_PROFILE
# load all parameters
def load_user_profile(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_fname, user_lname, gender, age, height, weight, activity_level, cal_targ, diet_id, user_id" \
          " FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql1, (email,))
    basic_info = mycursor.fetchall()
    sql2 = "SELECT diet_name FROM foodSystem.diets where diet_id=%s;"
    mycursor.execute(sql2, (basic_info[0][8],))
    diet = mycursor.fetchall()
    sql3 = "SELECT allergy_name FROM foodSystem.user_allergies ua join " \
           "foodSystem.allergies_or_sensitivity aos on ua.allergy_id=aos.allergy_id where user_id=%s;"
    mycursor.execute(sql3, (basic_info[0][9],))
    all_allergies = mycursor.fetchall()
    allergies =[]
    for al in all_allergies:
        allergies.append(al[0])
    return basic_info[0][0], basic_info[0][1], basic_info[0][2], basic_info[0][3], basic_info[0][4], basic_info[0][5],\
           basic_info[0][6], basic_info[0][7], diet[0][0], allergies

#user=load_user_profile('roni_zarfati@gmail.com')
#print(user)

def update_wegiht(email, weight):
    mydb = connect()
    mycursor = mydb.cursor()
    user_id = load_user_id(email)
    sql = "UPDATE foodSystem.users SET weight = %s WHERE user_id=%s;"
    mycursor.execute(sql, (weight,user_id))
    mydb.commit()


#update_wegiht('roni_zarfati@gmail.com',57)


## SEARCH
def load_ingredient(search_value):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT fi_name,fi_amount,fi_cal,fi_carb,fi_fat,fi_protein,fi_sugar" \
          " FROM foodSystem.food_ingredients where fi_name=%s;"
    mycursor.execute(sql, (search_value,))
    result = mycursor.fetchall()
    if result == []:
        return False
    return result

#g=load_ingredient('דבש')
#print(g[0])

def load_dish(search_value):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT dish_name,dish_cal,dish_carb,dish_fat,dish_protein FROM foodSystem.dishes where dish_name like %s;"
    search_value = ['%'+search_value+'%']
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
    search_value = ['%' + search_value + '%']
    mycursor.execute(sql, search_value)
    result = mycursor.fetchall()
    if result == []:
        return False
    return result



