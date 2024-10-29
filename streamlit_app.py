# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your current smoothie.")

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input("Name of Smoothie")
st.write("The name of your smoothie will be: ", name_on_order)

# Retrieve fruit options and convert to a list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()
fruit_options = my_dataframe['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# Create ingredients string for database insertion
ingredients_string = ' '

# Independent API call to fetch and display nutrition information
if ingredients_list:
    try:
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        if fruityvice_response.status_code == 200:
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Error: Received status code {fruityvice_response.status_code} from the API.")
    except requests.RequestException as e:
        st.error(f"Error fetching data from Fruityvice API: {e}")

# Button to submit order (independent of the API)
time_to_insert = st.button('Submit Order')

# Process order submission on button click
if time_to_insert:
    if ingredients_string:
        # Prepare and execute SQL statement
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f'Your {name_on_order} is ordered!', icon="✅")
    else:
        st.error("Please select ingredients before submitting the order.")
