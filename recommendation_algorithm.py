import sql_manager


## RECOMMENDATION ALGORITHM:
def create_user_rates_dictionary():
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    sql1 = "SELECT user_id FROM foodSystem.users;"
    mycursor.execute(sql1)
    all_users_id = mycursor.fetchall()
    data = {}
    for user in all_users_id:
        print(user[0])
        sql2= "select history_user_id,history_menu_id,avg_rate " \
              "FROM (SELECT history_user_id,history_menu_id,avg_rate,date," \
              "(RANK() OVER (PARTITION BY history_user_id,history_menu_id ORDER BY date desc)) as rank_row" \
              "FROM foodSystem.menu_history) as t" \
              "where (t.rank_row=1) and (t.history_user_id=%s);"
        mycursor.execute(sql2,((user[0]),))
        history_rates = mycursor.fetchall()
        print(history_rates)
        for menu in history_rates:
            #date[user[0]] = {menu[1]:menu[2]}
            pass

#create_user_rates_dictionary()

def pearson_corelation():
    pass

def user_parameters_similarity():
    pass

def check_user_allergy(email,menu):
    mydb = sql_manager.connect()
    mycursor = mydb.cursor()
    user_id = sql_manager.load_user_id(email)
    print(user_id)
    sql = "SELECT allergy_id,ingreAllergy_fi_id" \
          "FROM ((foodSystem.user_allergies ua join foodSystem.ingredients_in_allergies iia) on ua.allergy_id=iia.ingreAllergy_allergy_id)" \
          "where user_id=%s;"
    mycursor.execute(sql, (user_id))
    food_ingredients = mycursor.fetchall()
    print(food_ingredients)

#check_user_allergy('lior_arieli@gmail.com',1)
