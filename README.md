# Recipe Dashboard: Interactive Data Pipeline for Home Chefs

### Abstract
As an avid home chef, I often get stumped at the start when deciding what new recipe I want to try. When I also try to consider the nutrition and climate impacts of my recipe choice the decision can feel all the more daunting. And I'm [not the only one](https://www.nytimes.com/interactive/2019/04/30/dining/climate-change-food-eating-habits.html). This app is designed to alleviate that challenge. Using recipes sourced from popular home chef [What's Gaby Cooking](https://whatsgabycooking.com/), not only does it suggest new, random recipes for you to try - with detailed instructions and ingredients - it also combines data from two powerful APIs to extract nutrition and carbon dioxide emissions (co2e) for the constituent ingredients. This allows users to have a clear view of the impact of their meal choices. And if they don't like their first option, they can always click for more!

The final dashboard can be viewed [here](https://share.streamlit.io/srobbins-13/recipe_climate_nutrition_impact/recipe_dashboard_app.py).

### Design
This app is designed for casual to dedicated home chefs who want to dive deeper into their craft. It provides detailed information on nutrients (e.g. Fats, Carbs, Proteins, etc.) and the environmental impact of different ingredients/ingredient categories.

### Data
- ~1200 unique recipes were scraped from [whatsgabycooking.com](https://whatsgabycooking.com/) -> response dict with ~20-40 features each
- ~8000 unique ingredient API calls -> response dict with ~40 features each
- ~80 unique ingredient category API calls -> response dict with ~10 features each

### Algorithms
- Standardized and cleaned data from multiple sources
- Functions to call APIs for unique ingredients nutrition
- Functions to call APIs for emissions based on ingredient category and quantity
- Joining several disparate datasets to create useful collections for MongoDB

### Tools
- Data Collection: BeautifulSoup, Requests, Climitiq API, Spoonacular API
- Data Storage: MongoDB (Atlas), pyMongo
- Data Processing: pandas, numpy
- Data Visualization: plotly
- Web App Deployment: Streamlit

### Communication
I completed a 5-minute presentation of my data pipeline and recipe dashboard. All visuals and slides are included in this repository.
