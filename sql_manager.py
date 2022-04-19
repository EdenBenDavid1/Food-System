import mysql.connector

# CONNECT TO DB
def connect():
    mydb = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='FoodSystem')
    return mydb

email = 'roni_zarfati@gmail.com'


## WELCOME
# Check if email and password are exist
def check_login_user(email,password):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT email, password FROM FoodSystem.users WHERE email=%s and password=%s;"
    user = (email,password)
    mycursor.execute(sql, user)
    result = mycursor.fetchall()
    # if result is empty- Not found:
    if result == []:
        return False
    else:
        return True

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
def loat_parameters_from_menu(menu):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT round(menu_cal,2),round(menu_carb,2),round(menu_protein,2),round(menu_fat,2) " \
          "FROM foodSystem.menus WHERE menu_id=%s;"
    mycursor.execute(sql, (menu,))
    result = mycursor.fetchall()
    return result

#parameters = loat_parameters_from_menu(1)
#for para in parameters:
#    print(parameters)

# After the algorithm suggest a daily menu, show the update values, according to what the user ate:
def load_update_values():
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "select round(sum(meal_cal),2),round(sum(meal_carb),2),round(sum(meal_protein),2),round(sum(meal_fat),2) " \
          "from foodSystem.rates r join foodSystem.meals m on r.rates_meal_id=m.meal_id where date=current_date();"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    # id the user didn't eat anything yet:
    if result == [(None, None, None, None)]:
        result = [(0,0,0,0)]
    return result

#values = load_update_values()
#for val in values:
#print(values)

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



