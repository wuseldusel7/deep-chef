import pandas as pd 
import random
import numpy as np 
import os
import re
import json
import ast
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import Embedding, Dense, LSTM, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping



def text_generator(ingredients):

    df = pd.read_csv('recipe_list.csv')

    tokenizer_ = {}
    max_sequence_len_ = {}


    df_seed = pd.read_csv('seed_words.csv')
    df_seed.drop('Unnamed: 0', axis=1, inplace=True)

    num_of_words = [25,14,14,16,13,15,15,14,16,16,15,16,15,16,15,14,16,15,14,15, 14, 15,15,18,16,15,15,8,4]

    # generate seed words
    num_of_ingredients = len(ingredients)
    instruction_steps = round(num_of_ingredients * 1.32 + 7.6) + random.randint(-3,2)



    output_ = []
    for gen_cycle in range(instruction_steps):


        data = []
        num_of_samples = 352
        df_ = df.sample(num_of_samples, random_state=42)
        for i in range(len(df_)):
            try:
                data.append(ast.literal_eval(df_.reset_index().instruction_dict[i])[gen_cycle].lower())
            except:
                data.append("")

        
        
        tokenizer_[f"{gen_cycle}"] = Tokenizer()
        tokenizer_[f"{gen_cycle}"].fit_on_texts(data)
        #total_words = len(tokenizer_[f"{gen_cycle}"].word_index) + 1

        input_sequences = []
        for line in data:
            token_list = tokenizer_[f"{gen_cycle}"].texts_to_sequences([line])[0]
            for i in range(1, len(token_list)): 
                n_gram_sequence = token_list[:i+1]
                input_sequences.append(n_gram_sequence)

        max_sequence_len_[f"{gen_cycle}"] = max([len(x) for x in input_sequences])




        model = load_model(f'models/model_{gen_cycle}_iter.h5')

        
    
        seed_text = df_seed[f'{gen_cycle}'].dropna().sample(1).tolist()[0].lower().lstrip(f'{gen_cycle}: ')


        next_words = num_of_words[gen_cycle] + random.randint(-10,5)

        for _ in range(next_words):
            token_list = tokenizer_[f"{gen_cycle}"].texts_to_sequences([seed_text])[0]
            token_list = pad_sequences([token_list], maxlen=max_sequence_len_[f"{gen_cycle}"]-1, padding='pre')
            predict_x=model.predict(token_list, verbose=0) 
            classes_x=np.argmax(predict_x,axis=1)
            output_word = ""
            for word, index in tokenizer_[f"{gen_cycle}"].word_index.items():
                if index == classes_x:
                    output_word = word
                    break
            seed_text += " " + output_word
        
        output_.append(seed_text)




    path_to_glove_file = os.path.join(
        os.path.expanduser(""), "glove.6B.100d.txt"
    )

    embeddings_index = {}
    with open(path_to_glove_file) as f:
        for line in f:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            embeddings_index[word] = coefs




    cosine_loss = tf.keras.losses.CosineSimilarity(axis=1)
    unknown_words = []

    out_lst = []

    for outpt in output_:
        out = outpt.split()    #['11:', 'do', 'water', 'eggplant', 'water', 'water', 'a', '¼', '24']

        for j, word in enumerate(out):

            for i, ing in enumerate(ingredients):
                try:
                    loss = - cosine_loss([embeddings_index[word].tolist()], [embeddings_index[ing].tolist()]).numpy()
                    if loss > 0.55:
                        out[j] = ing
                            
                except:
                    unknown_words.append(word)
        s = str()
        for word_ in out:
            s += word_ + ' '

        out_lst.append(s)
    
    return out_lst


if __name__ == "__main__":
    ingredients = ['onions', 'paprika', 'lattice', 'salt', 'pepper', 'garlilc']
    text_generator(ingredients)


