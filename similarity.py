# import necessary libraries

import pandas as pd
from math import sqrt


# dictionary with usernames their watched web series and ratings out of 5
dataset = {
    'Tanya': {'Special Ops': 5,
              'Criminal Justice': 3,
              'Panchayat': 3,
              'Sacred Games': 3,
              'Apharan': 2,
              'Mirzapur': 3},

    'Mohan': {'Special Ops': 5,
              'Criminal Justice': 3,
              'Sacred Games': 5,
              'Panchayat': 5,
              'Mirzapur': 3,
              'Apharan': 3},

    'Tasha': {'Special Ops': 2,
              'Panchayat': 5,
              'Sacred Games': 3,
              'Mirzapur': 4},

    'Nirbhay': {'Panchayat': 5,
                'Mirzapur': 4,
                'Sacred Games': 4, },

    'Muskan': {'Special Ops': 4,
               'Criminal Justice': 4,
               'Panchayat': 4,
               'Mirzapur': 3,
               'Apharan': 2},

    'Anshika': {'Special Ops': 3,
                'Panchayat': 4,
                'Mirzapur': 3,
                'Sacred Games': 5,
                'Apharan': 3},

    'Dhawal': {'Panchayat': 4,
               'Apharan': 1,
               'Sacred Games': 4}}


#create a data frame of this dataset
dataset_df=pd.DataFrame(dataset)
dataset_df.fillna("Not Seen Yet",inplace=True)
#print(dataset_df)

# custom function to create unique set of web series
def unique_items():
    unique_items_list = []
    for person in dataset.keys():
        for items in dataset[person]:
            unique_items_list.append(items)
    s=set(unique_items_list)
    unique_items_list=list(s)
    return unique_items_list

u = unique_items()
#print(u)

# custom function to create pearson correlation method from scratch
def person_corelation(person1,person2):
    both_rated = {}
    for item in dataset[person1]:
        if item in dataset[person2]:
            both_rated[item] = 1

    number_of_ratings = len(both_rated)
    if number_of_ratings == 0:
        return 0

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

p = person_corelation('Tanya','Anshika')
#print(p)

# custom function to check most similar users
def most_similar_users(target_person, no_of_users):
    # Used list comprehension for finding pearson similarity between users
    scores = [(person_corelation(target_person, other_person), other_person) for other_person in dataset if
              other_person != target_person]

    # sort the scores in descending order
    scores.sort(reverse=True)

    # return the scores between the target person & other persons
    return scores[0:no_of_users]

# function check by input one person name & returns the similarity score
m = most_similar_users('Nirbhay',6)
print(m)


#custom function to filter the seen movies and unseen movies of the target user
def target_movies_to_users(target_person):
    target_person_movie_lst = []
    unique_list =unique_items()
    for movies in dataset[target_person]:
        target_person_movie_lst.append(movies)

    s=set(unique_list)
    recommended_movies=list(s.difference(target_person_movie_lst))
    a = len(recommended_movies)
    if a == 0:
        return 0,target_person_movie_lst
    return recommended_movies,target_person_movie_lst


# function check
unseen_movies,seen_movies=target_movies_to_users('Tanya')
print(unseen_movies,seen_movies)


def recommendation_phase(person):
    # Gets recommendations for a person by using a weighted average of every other user's rankings
    totals = {}  #empty dictionary
    simSums = {} # empty dictionary
    for other in dataset:
        # don't compare me to myself
        if other == person:
            continue
        sim = person_corelation(person, other)

        # ignore scores of zero or lower
        if sim <= 0:
            continue
        print('kkkkkk' , other)
        for item in dataset[other]:
            # only score movies i haven't seen yet
            #if item not in dataset[person]:
            print(item)
            # Similrity * score
            totals.setdefault(item, 0)
            totals[item] += dataset[other][item] * sim
            print(totals)
            # sum of similarities
            simSums.setdefault(item, 0)
            simSums[item] += sim
            print(simSums)
            # Create the normalized list

    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort(reverse=True)
    print(rankings)
    # returns the recommended items
    recommendataions_list = [(recommend_item,score) for score, recommend_item in rankings]
    return recommendataions_list


tp = 'Nirbhay'
if tp in dataset.keys():
    a=recommendation_phase(tp)
    if a != -1:
        print("Recommendation Using User based Collaborative Filtering:  ")
        for webseries,weights in a:
            print(webseries,'---->',weights)
else:
    print("Person not found in the dataset..please try again")