

''' This document is hosted on github and is the source for a Streamlit App.
The following code is broken into sections based on the user experience of the app. The sections
are as follows:
- Data Setup
- Section 1: Intro & Welcome Text

'''




# Data Setup
import pandas as pd
import numpy as np
import streamlit as st
import pymongo
from pymongo import MongoClient
import random
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# Setting up streamlit page
st.set_page_config(
            page_title = 'Recipe Dashboard',
            layout="wide")


#connect to cloud Mongodb server
database_name = 'RecipeData'

client = MongoClient("mongodb+srv://srobbins13:yFgUZTu1s3RLqo6c@recipecluster.qtpe1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client[database_name]

# create list of recipe titles to pull random recipe from
recipe_list = list(db.recipes_totals.find({}))
recipe_titles = []

for entry in recipe_list:
    recipe_titles.append(entry['recipe'])


##############################################
# Setting up the Sidebar of the page with Intro and Welcome Text
st.sidebar.title('Welcome to the WhatsGabyCooking Interactive Dashboard!')
st.sidebar.markdown("""
<medium>This app is for those who love to cook but can't for the life of them decide what to make. Users will be provided a random recipe - with ingredients and instuctions - in addition to useful graphics on the nutrition breakdown of the recipe and the carbon emissions it takes to produce. With over 1000 unique recipes for the app to choose from, feel free to loop through until you find a recipe you like, with a footprint you can feel good about. Happy Cooking!</medium>""",unsafe_allow_html = True)


st.sidebar.header("Choose a random recipe below:")

# initialize the recipe instance
target_recipe = None

if st.sidebar.button('Hit for Random Recipe'):
    target_recipe = random.choice(recipe_titles)

st.sidebar.header("Disclaimer")
st.sidebar.info('All recipes presented here are the sole IP and trademarks of [whatsgabycooking.com](https://whatsgabycooking.com/)')


##############################################

# Gather data for `target_recipe`
if target_recipe:
    text = list(db.recipes_text.find({'title':target_recipe}).limit(1))[0]
    totals = list(db.recipes_totals.find({'recipe':target_recipe}).limit(1))[0]
    categories = list(db.recipes_categories.find({'recipe':target_recipe}))

    # Dashboard
    st.title(f'Dashboard for {target_recipe}')

    ###########
    # Set up dashboard layout
    c1,c2,c3,c4 = st.columns((1.5,1.5,2,2))

    c1.header('Ingredients')

    ingredient_dict = text['ingredients']
    ingredient_list = []
    for entry in ingredient_dict:
        ing_str = [entry['amount'],entry['unit'],entry['name']]
        ing_str = [i for i in ing_str if i]
        c1.markdown(" ".join(ing_str))


    c1.image('https://media.istockphoto.com/vectors/vector-illustration-woman-cooking-vector-id1222105326?k=20&m=1222105326&s=170667a&w=0&h=rdpni0nbMjAqM85Yk_YHI9Aaye8HS7V0BCd4W1DD3eI=')

    ###########
    c2.header('Instructions')

    instruction_list = text['instructions']
    for val in instruction_list:
        c2.markdown(val)


    ###########
    # Get total nutrition values for the recipes
    total_fat = np.round(totals['Fat'],2)
    total_sodium = np.round(totals['Sodium'],2)
    total_net_carb = np.round(totals['Net_Carbs'],2)
    total_chol = np.round(totals['Cholesterol'],2)
    total_carbs = np.round(totals['Carbohydrates'],2)
    total_sat_fat = np.round(totals['Sat_Fat'],2)
    total_cal = np.round(totals['Calories'],2)
    total_sug = np.round(totals['Sugar'],2)
    total_prot = np.round(totals['Protein'],2)
    total_co2e = np.round(totals['co2e_actual'],2)

    # Get Nutrition Information for recipe ingredients
    category_labels = []
    fat_values = []
    carb_values = []
    protein_values = []
    co2e_values = []

    for cat in categories:
        category_labels.append(cat['emission_ID'])
        fat_values.append(cat['Fat'])
        carb_values.append(cat['Carbohydrates'])
        protein_values.append(cat['Protein'])
        co2e_values.append(cat['co2e_actual'])

    # clean up the labels
    labels_clean = []

    for label in category_labels:
        category = label.split('-')
        category = category[1]
        labels_clean.append(category.replace('type_','').replace('_',', '))


    # Plots
    c3.header('Fat Breakdown')
    fat_label = f'{total_fat} g'
    fig1 = go.Figure(data=[go.Pie(labels=labels_clean, values=fat_values,
                             marker_colors = px.colors.diverging.Portland, hole=.4,
                             hovertemplate = "%{label}: <br>%{value} g <br>%{percent} of meal</br><extra></extra>")])

    fig1.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                        annotations=[dict(text=fat_label, x=0.5, y=0.45, font_size=20, showarrow=False),
                                     dict(text='Total Fat', x=0.5, y=0.55, font_size=20, showarrow=False)],
                        hoverlabel= dict(
                                    bgcolor="white",
                                    font_size=18))
    c3.plotly_chart(fig1)

    c3.header('Carbohydrates Breakdown')

    fig2 = go.Figure(data=[go.Pie(labels=labels_clean, values=carb_values,
                             marker_colors = px.colors.diverging.RdYlBu, hole=.4,
                             hovertemplate = "%{label}: <br>%{value} g <br>%{percent} of meal</br><extra></extra>")])

    carb_label = f'{total_carbs} g'
    fig2.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                        annotations=[dict(text=carb_label, x=0.5, y=0.45, font_size=20, showarrow=False),
                                     dict(text='Total Carbs', x=0.5, y=0.55, font_size=20, showarrow=False)],
                        hoverlabel= dict(
                                    bgcolor="white",
                                    font_size=18))
    c3.plotly_chart(fig2)

    ###########
    c4.header('Protein Breakdown')
    prot_label = f'{total_prot} g'
    fig3 = go.Figure(data=[go.Pie(labels=labels_clean, values=protein_values,
                             marker_colors = px.colors.diverging.Armyrose, hole=.4,
                             hovertemplate = "%{label}: <br>%{value} g <br>%{percent} of meal</br><extra></extra>")])

    fig3.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                        annotations=[dict(text=prot_label, x=0.5, y=0.45, font_size=20, showarrow=False),
                                     dict(text='Total Protein', x=0.5, y=0.55, font_size=20, showarrow=False)],
                        hoverlabel= dict(
                                    bgcolor="white",
                                    font_size=18))
    c4.plotly_chart(fig3)

    c4.header('CO2E Breakdown')
    co2e_label = f'{total_co2e} kg'
    fig4 = go.Figure(data=[go.Pie(labels=labels_clean, values=co2e_values,
                             marker_colors = px.colors.cyclical.Twilight, hole=.4,
                             hovertemplate = "%{label}: <br>%{value} kg <br>%{percent} of meal</br><extra></extra>")])
    fig4.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                        annotations=[dict(text=co2e_label, x=0.5, y=0.45, font_size=20, showarrow=False),
                                     dict(text='Total CO2E', x=0.5, y=0.55, font_size=20, showarrow=False)],
                        hoverlabel= dict(
                                    bgcolor="white",
                                    font_size=18))
    c4.plotly_chart(fig4)

    ###########
    #st.header('here is another long chart')
