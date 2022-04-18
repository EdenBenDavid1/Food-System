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


def load_x():
    pass

def save_x():
    pass

def update_x():
    pass
