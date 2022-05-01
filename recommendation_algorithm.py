import sql_manager
from math import sqrt

## RECOMMENDATION ALGORITHM:

# create a user rates dictionary only to users that rated menus
def create_user_rates_dictionary():
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_id FROM foodSystem.users;"
    mycursor.execute(sql1)
    all_users_id = mycursor.fetchall()
    all_data = {}
    for user in all_users_id:
        sql2= "select history_menu_id,avg_rate " \
              "FROM (SELECT history_user_id,history_menu_id,avg_rate,date," \
              "(RANK() OVER (PARTITION BY history_user_id,history_menu_id ORDER BY date desc)) as rank_row " \
              "FROM foodSystem.menu_history) as t " \
              "where (t.rank_row=1) and (t.history_user_id=%s);"
        mycursor.execute(sql2,((user[0]),))
        history_rates = mycursor.fetchall()
        inside_dic = {} # every user has his own menus, rebut every user
        for history in history_rates:
            inside_dic[history[0]]=history[1] # dict for menu:rate
            all_data[user[0]] = inside_dic # user has -  menu:rate
    print(all_data)
    return all_data

#create_user_rates_dictionary()

# check the rates correlation between 2 users
def pearson_correlation(person1, person2):
    dataset = create_user_rates_dictionary()
    # To get both rated items
    both_rated = {}
    for item in dataset[person1]:
        if item in dataset[person2]:
            both_rated[item] = 1
    number_of_ratings = len(both_rated)
    # Checking for number of ratings in common
    if number_of_ratings == 0:
        return 0
    # Add up all the preferences of each user
    person1_preferences_sum = sum([dataset[person1][item] for item in both_rated])
    person2_preferences_sum = sum([dataset[person2][item] for item in both_rated])
    # Sum up the squares of preferences of each user
    person1_square_preferences_sum = sum([pow(dataset[person1][item], 2) for item in both_rated])
    person2_square_preferences_sum = sum([pow(dataset[person2][item], 2) for item in both_rated])
    # Sum up the product value of both preferences for each item
    product_sum_of_both_users = sum([dataset[person1][item] * dataset[person2][item] for item in both_rated])
    # Calculate the pearson score
    numerator_value = product_sum_of_both_users - (
                person1_preferences_sum * person2_preferences_sum / number_of_ratings)
    denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum, 2) / number_of_ratings) * (
                person2_square_preferences_sum - pow(person2_preferences_sum, 2) / number_of_ratings))
    if denominator_value == 0:
        return 0
    else:
        r = numerator_value / denominator_value
        return r

#correlation = pearson_correlation(1, 5)
#print(correlation)

def get_user_info(user):
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    sql = "SELECT gender, birth_date, weight, height, activity_level, diet_id, gain_keep_lose" \
           " FROM FoodSystem.users WHERE user_id=%s;"
    mycursor.execute(sql, (user,))
    basic_info = mycursor.fetchall()[0]
    age = sql_manager.calc_age(basic_info[1])
    user_info = [basic_info[0],age,basic_info[2],basic_info[3],basic_info[4],basic_info[5],basic_info[6]]
    return user_info

#b = get_user_info(1)
#print(b)

# for all calculations:
def calc_attribute(attribute1,attribute2):
    return 1 / (abs(attribute1-attribute2)+1)

# gender
def gender_attribute(user1,user2):
    if user1 == user2:
        gender = 1
    else:
        gender = 0
    return gender

# age
def age_groups(parameter):
    if parameter <= 20:
        return 1
    elif parameter > 20 and parameter <= 40:
        return 2
    else:
        return 3

def age_attribute(user1,user2):
    age1 = age_groups(user1)
    age2 = age_groups(user2)
    age = calc_attribute(age1,age2)
    return age

#weight
def weight_groups(parameter):
    if parameter <= 50:
        return 1
    elif parameter > 50 and parameter <= 60:
        return 2
    elif parameter > 60 and parameter <= 70:
        return 3
    elif parameter > 70 and parameter <= 80:
        return 4
    elif parameter > 80 and parameter <= 90:
        return 5
    else:
        return 6

def weight_attribute(user1,user2):
    weight1 = weight_groups(user1)
    weight2 = weight_groups(user2)
    weight = calc_attribute(weight1,weight2)
    return weight

# height
def height_groups(parameter):
    if parameter <= 150:
        return 1
    elif parameter > 150 and parameter <= 160:
        return 2
    elif parameter > 160 and parameter <= 170:
        return 3
    elif parameter > 170 and parameter <= 180:
        return 4
    elif parameter > 180 and parameter <= 190:
        return 5
    else:
        return 6

def height_attribute(user1,user2):
    height1 = height_groups(user1)
    height2 = height_groups(user2)
    height = calc_attribute(height1,height2)
    return height

# activity level
def activity_groups(parameter):
    if parameter == 'ללא אימונים':
        return 1
    elif parameter == '1-3 אימונים בשבוע':
        return 2
    elif parameter == '4-5 אימונים בשבוע':
        return 3
    elif parameter == '6-7 אימונים בשבוע':
        return 4
    else:
        return 5

def activity_attribute(user1,user2):
    activity_level1 = activity_groups(user1)
    activity_level2 = activity_groups(user2)
    activity_level = calc_attribute(activity_level1,activity_level2)
    return activity_level

# diet
def diet_attribute(user1,user2):
    if user1 == user2:
        diet = 1
    else:
        diet = 0
    return diet

# weight target
def target_groups(parameter):
    if parameter == 'להוריד במשקל':
        return 1
    elif parameter == 'לשמור על המשקל':
        return 2
    else:
        return 3

def target_attribute(user1,user2):
    target_weight1 = target_groups(user1)
    target_weight2 = target_groups(user2)
    target_weight = calc_attribute(target_weight1,target_weight2)
    return target_weight

# check the attributes similarity between 2 users
def user_parameters_similarity(person1,person2):
    user_info_1 = get_user_info(person1)
    user_info_2 = get_user_info(person2)

    gender = gender_attribute(user_info_1[0],user_info_2[0])
    age = age_attribute(user_info_1[1],user_info_2[1])
    weight = weight_attribute(user_info_1[2],user_info_2[2])
    height = height_attribute(user_info_1[3], user_info_2[3])
    activity_level = activity_attribute(user_info_1[4], user_info_2[4])
    diet = diet_attribute(user_info_1[5], user_info_2[5])
    target_weight = target_attribute(user_info_1[6], user_info_2[6])

    similarity_attribute = (0.3*gender + 0.2*diet + 0.14*activity_level + 0.09*weight + 0.09*height + 0.09*age + 0.09*target_weight)
    return similarity_attribute

attribute = user_parameters_similarity(10,12)
print(attribute)

# calc the weighted similarity of the 2 similarities
def weighted_similarity():
    pass

# return a list with menus for a specific user, based on the weighted similarity, and the same diet
def knn(person): # person - that we want to do for him recomendation
    dataset = create_user_rates_dictionary()
    for other in dataset:
        # don't compare me to myself
        if other == person:
            continue
        if person not in dataset.keys(): # new user in the system, without rates
            weighted_similarity = 1 * user_parameters_similarity(person,other)
        else:
            weighted_similarity = 0.7 * user_parameters_similarity(person,other) + 0.3 * pearson_correlation(person,other)




def recommendation_algorithm(person):
    if person == 1:
        return 2
    else:
        return 3


# check if the recommended menu has any of user allergies
def check_user_allergy(email,menu_id_recommend):
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    user_id = sql_manager.load_user_id(email)
    sql = "SELECT allergy_id,ingreAllergy_fi_id " \
          "FROM foodSystem.user_allergies ua join foodSystem.ingredients_in_allergies iia " \
          "on ua.allergy_id=iia.ingreAllergy_allergy_id " \
          "where user_id=%s;"
    mycursor.execute(sql, (user_id,))
    food_ingredients = mycursor.fetchall()
    print(food_ingredients)
    if food_ingredients == []: # the user has not allergy, he can use the recommended menu
        return True
    else: # the user has 1 or more allergies:
        food_id_list = []
        for food in food_ingredients:
            food_id_list.append(food[1]) # all the food ingredients in a list
        t = tuple(food_id_list)
        sql2 = "select distinct(menu_id) " \
               "from (((foodSystem.menus m " \
               "join foodSystem.meals_in_menu mim on m.menu_id=mim.mealsInMenu_menu_id) " \
               "join  foodSystem.dish_in_meal dim on mim.mealsInMenu_meal_id=dim.dishInMeal_meal_id) " \
               "join foodSystem.ingredients_in_dish ind on dim.dishInMeal_dish_id=ind.dish_id)" \
               "where fi_id IN {};".format(t)
        mycursor.execute(sql2)
        all_menus = mycursor.fetchall() # all menus the user can't eat because his allergy
        print("menus the user can't eat:",all_menus)
        for menu in all_menus:
            if menu[0] == menu_id_recommend:
                return False
            else:
                return True

#a = check_user_allergy('ariel_cohen@gmail.com',2)
#print(a)

def check_menu_calories_range(email,menu_id_recommend):
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT cal_targ FROM foodSystem.users where email=%s;"
    mycursor.execute(sql1, (email,))
    user_cal = mycursor.fetchall()[0][0]
    sql2 = "SELECT menu_cal FROM foodSystem.menus where menu_id=%s;"
    mycursor.execute(sql2, (menu_id_recommend,))
    menu_cal = mycursor.fetchall()[0][0]
    if (menu_cal >= user_cal-150) and (menu_cal <= user_cal+150):
        # if the menu that recommended in the range of calories the user can eat
        return True
    else:
        return False

g = check_menu_calories_range('roni_zarfati@gmail.com',1)
print(g)

