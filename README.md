# deep-chef
Recipe recommender/creator based on given ingredients


This is a work in progress project. 

`scraper.py`: Scrapes data from recipes from the homepage https://www.giallozafferano.it and safes a csv file.

`recipe_finder.py`: This finds similarities between user input ingredients and ingredients of a given recipe by using word embedding and vectorization

`recipe_generator_2_0.py`: This trains several RNN-LSTM Models to generate unique recipes from more than 350 recipe insturction texts from                                                      https://www.giallozafferano.it, also including the user ingredients input.

`final_project_app.py` : This creates the streamlit server to create a user interface.
                           

