import pandas as pd 
import random
import numpy as np 
import os
import re
import json
import ast
import matplotlib.pyplot as plt
import tensorflow as tf



path_to_glove_file = os.path.join(
    os.path.expanduser(""), "glove.6B.100d.txt"
)
embeddings_index = {}
with open(path_to_glove_file) as f:
    for line in f:
        word, coefs = line.split(maxsplit=1)
        coefs = np.fromstring(coefs, "f", sep=" ")
        embeddings_index[word] = coefs



def string_to_list(s):
    '''Converting string to a list of floats '''
    vec = s.replace("\n", "").replace("[", "").replace("]", "")
    floats_list = []
    for item in vec.split():
        floats_list.append(float(item))
    return floats_list



def vector_sum(lst):
    ''' Calculate sum of several vectors
    '''
    lst_matrix = np.zeros((len(lst), 100))
    for i in range(len(lst)):
        try:
            lst_matrix[i][:] = embeddings_index[lst[i]]
        except:
            lst_matrix[i][:] = np.zeros((1,100))
    vec_sum = lst_matrix.T.sum(axis=1).T
    norm = np.linalg.norm(vec_sum)
    norm_vec_sum = vec_sum/norm

    return norm_vec_sum


df = pd.read_csv('recipe_list.csv')

ingredients_vector_sum = []
for j in range(len(df)):
    ingr_lst = []
    for i in range(len(ast.literal_eval(df.ingredients[j]))):
        for word in ast.literal_eval(df.ingredients[j])[i].split():
            ingr_lst.append(word)
    ingredients_vector_sum.append(vector_sum(ingr_lst))

df['ingredients_vector_sum'] = ingredients_vector_sum



def get_matching_url(ingredients):

    cosine_loss = tf.keras.losses.CosineSimilarity(axis=1)

    key = []
    value = []
    for i in range(len(df)):
        vector_sum(ingredients)
        sim = - cosine_loss([df.ingredients_vector_sum[i].tolist()], [vector_sum(ingredients).tolist()]).numpy()
        key.append(i)
        value.append(sim)
    
    d = dict(zip(key, value))
    return df.iloc[max(d, key=d.get)]['url']

if __name__ == '__main__':
    ingredients = ['onion', 'seeds', 'lattice', 'water', 'pepper', 'salt', 'eggplant', 'beef', 'shark']
    get_matching_url(ingredients)
