import mysql.connector

# CONNECT TO DB
def connect():
    mydb = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='FoodSystem')
    return mydb

# ------ EXAMPLE
def load_data_example():
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT sum(fi_cal*amount), sum(fi_carb*amount), sum(fi_fat*amount), sum(fi_protein*amount), sum(fi_sugar*amount)"
        "FROM FoodSystem.food_ingredients join FoodSystem.ingredients_in_dish on(food_ingredients.fi_id=ingredients_in_dish.fi_id) "
        "WHERE dish_id=1;")
    result = mycursor.fetchall()
    return result

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
def load_user(email):
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT user_fname, user_lname, cal_targ, email FROM FoodSystem.users WHERE email=%s;"
    mycursor.execute(sql, (email,))
    result = mycursor.fetchall()
    return result[0][0], result[0][1], result[0][2]


## MY_PROFILE
def load_user_profile():
    mydb = connect()
    mycursor = mydb.cursor()
    sql = "SELECT user_fname, user_lname, gender, age,height, weight, activity_level, cal_targ" \
          " FROM FoodSystem.users WHERE user_id=1;"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7]

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
    #return result[0][0], result[0][1], result[0][2], result[0][3], result[0][4]

ingredient=load_ingredient('דבש')
#for ing in ingredient:
#    print(ing[0])

dish = load_dish('מבושל')
for d in dish:
    print(d[0], d[1])



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



