

''' This document is hosted on github and is the source for a Streamlit App.
The following code is broken into sections based on the user experience of the app.
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
import matplotlib as plt

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
st.sidebar.image('https://cdn.whatsgabycooking.com/wp-content/uploads/2019/09/wgc-logo-large.png')
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
# dashboard won't display until recipe is chosen
if target_recipe:
    text = list(db.recipes_text.find({'title':target_recipe}).limit(1))[0]
    totals = list(db.recipes_totals.find({'recipe':target_recipe}).limit(1))[0]
    categories = list(db.recipes_categories.find({'recipe':target_recipe}))

    # Dashboard
    st.markdown(f"<h1 style='text-align: center'><u>{target_recipe}</u></h1>", unsafe_allow_html=True)

    ###########
    # Set up dashboard layout
    # For ease of use in mobile formats, the dashboard will be arranged vertically

    st.markdown("<h2 style='text-align: center'>Ingredients</h2>", unsafe_allow_html=True)

    ingredient_dict = text['ingredients']
    ingredient_list = []
    for entry in ingredient_dict:
        ing_str = [entry['amount'],entry['unit'],entry['name']]
        ing_str = [i for i in ing_str if i]
        ing_text = " ".join(ing_str)
        st.markdown(f"<p style='text-align: center'>{ing_text}</p>", unsafe_allow_html=True)

    ###########
    st.markdown("""---""")
    st.markdown("<h2 style='text-align: center'>Instructions</h2>", unsafe_allow_html=True)

    instruction_list = text['instructions']
    for val in instruction_list:
        st.markdown(f"<p style='text-align: center'>{val}</p>", unsafe_allow_html=True)


    ###########
    # Get nutrition values for recipe plots
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

    # Get Nutrition Information for ingredient categories from database dictionary
    category_labels = []
    fat_values = []
    sodium_values = []
    net_carb_values = []
    cholesterol_values = []
    carb_values = []
    sat_fat_values = []
    calories_values = []
    sugar_values = []
    protein_values = []
    co2e_values = []


    for cat in categories:
        category_labels.append(cat['emission_ID'])
        fat_values.append(cat['Fat'])
        sodium_values.append(cat['Sodium'])
        net_carb_values.append(cat['Net_Carbs'])
        cholesterol_values.append(cat['Cholesterol'])
        carb_values.append(cat['Carbohydrates'])
        sat_fat_values.append(cat['Sat_Fat'])
        calories_values.append(cat['Calories'])
        sugar_values.append(cat['Sugar'])
        protein_values.append(cat['Protein'])
        co2e_values.append(cat['co2e_actual'])

    # clean up the labels for plotting
    labels_clean = []

    for label in category_labels:
        category = label.split('-')
        category = category[1]
        labels_clean.append(category.replace('type_','').replace('_',', '))


    # Make dictionary with nutrient values for plots
    plot_options = list(totals.keys())[2:]

    plot_values = [fat_values,
                sodium_values,
                net_carb_values,
                cholesterol_values,
                carb_values,
                sat_fat_values,
                calories_values,
                sugar_values,
                protein_values,
                co2e_values]

    plot_totals = [total_fat,
                total_sodium,
                total_net_carb,
                total_chol,
                total_carbs,
                total_sat_fat,
                total_cal,
                total_sug,
                total_prot,
                total_co2e]

    units = ['g',
            'mg',
            'g',
            'mg',
            'g',
            'g',
            'kcal',
            'g',
            'g',
            'kg']

    plot_dict = dict(zip(plot_options, zip(plot_values, plot_totals,units)))

    # Plotting Function
    def make_pie_chart(plot_variable, color, title = None, inner_label = None, column = st):
        values = plot_dict.get(plot_variable)[0]
        total = plot_dict.get(plot_variable)[1]
        unit = plot_dict.get(plot_variable)[2]

        if title == None:
            column.markdown(f"<h3 style='text-align: center'>{plot_variable} Breakdown</h3>", unsafe_allow_html=True)
        else:
            column.markdown(f"<h3 style='text-align: center'>{title}</h3>", unsafe_allow_html=True)

        # making the figure
        fig = go.Figure(data=[go.Pie(labels=labels_clean, values=values,
                                 marker_colors = color, hole=.4,
                                 hovertemplate = "%{label}: <br>%{value} g <br>%{percent} of meal</br><extra></extra>")])

        # updating figure labels with total values
        if inner_label == None:
            fig.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                                annotations=[dict(text=f'{total} {unit}', x=0.5, y=0.45, font_size=20, showarrow=False),
                                             dict(text=f'Total {plot_variable}', x=0.5, y=0.55, font_size=20, showarrow=False)],
                                            hoverlabel= dict(
                                            bgcolor="white",
                                            font_size=18))
        else:
            fig.update_layout(legend_title = 'Ingredient Category', font = dict(size = 20),
                                annotations=[dict(text=f'{total} {unit}', x=0.5, y=0.45, font_size=20, showarrow=False),
                                             dict(text=inner_label, x=0.5, y=0.55, font_size=20, showarrow=False)],
                                            hoverlabel= dict(
                                            bgcolor="white",
                                            font_size=18))
        column.plotly_chart(fig)


    ###########
    # Starting with CO2E Plot
    st.markdown("""---""")
    st.markdown("<h2 style='text-align:center'>Environmental Impact of Recipe</h2>", unsafe_allow_html=True)
    make_pie_chart(plot_options[-1], px.colors.cyclical.Twilight, title = 'CO2 Emissions Breakdown', inner_label = 'Total CO2E')

    # Plot histogram of CO2E for entire database to compare target recipe to other values
    co2e_values = list(db.recipes_totals.find({},{'co2e_actual':1, '_id':0}))
    co2e_val_clean = []

    for val in co2e_values:
        co2e_val_clean.append(val['co2e_actual'])

    co2e_sorted = sorted(co2e_val_clean)

    larger_elements = [element for element in co2e_sorted if element > total_co2e]
    number_of_elements = len(larger_elements)

    st.markdown(f"<h4 style='text-align:center; color: gray'><em>This recipe has a lower carbon output than {number_of_elements} other recipes in the database</em></h4>", unsafe_allow_html=True)

    bin_list = list(range(0,80,2))

    fig,ax = plt.pyplot.subplots(figsize = (20,6),facecolor = 'black')
    ax.hist(co2e_sorted, bins = bin_list, edgecolor = 'white')
    ax.axvline(total_co2e, color = 'r', linestyle = 'dashed',linewidth = 4)
    ax.set_facecolor(color = 'black')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    plt.pyplot.xticks(fontsize = 15)
    plt.pyplot.yticks(fontsize = 15)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_ylabel('Frequency',fontsize = 20, c = 'white')
    ax.set_xlabel('CO2 Emissions (kg)',fontsize = 20, c = 'white')

    st.pyplot(fig)

    ###########
    # Plotting various nutrients
    st.markdown("""---""")
    st.markdown("<h2 style='text-align:center'>Nutrition Information</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'><em>Note: Nutrition values are for entire meal, not individual servings</em></p>", unsafe_allow_html=True)

    make_pie_chart(plot_options[0], px.colors.diverging.RdYlBu)
    make_pie_chart(plot_options[1], px.colors.diverging.Portland)
    make_pie_chart(plot_options[4], px.colors.diverging.Armyrose)
    make_pie_chart(plot_options[6], px.colors.diverging.RdYlBu)
