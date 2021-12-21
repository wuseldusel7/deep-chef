import streamlit as st 
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import plotly.express as px

import recipe_generator_2_0 as rg
import recipe_finder as rf


st.title('DEEP CHEF')

ingredients = st.text_input('Enter your ingredients here')

st.markdown('By pressing `Find recipe` you will get a delicious recipe based on your list of ingredients.')

if st.button('Find recipe'):
    result = rf.get_matching_url(ingredients.split(','))
    st.write('There you go: %s' % result)


st.markdown('Press `Generate unique recipe` and let the computer decide how you should cook.')

if st.button('Generate unique recipe'):
    recipe = rg.text_generator(ingredients.split(','))
    st.write(recipe)


