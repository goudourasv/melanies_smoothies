import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your current smoothie.")

# Establish Snowflake connection
cnx = st.experimental_connection("snowflake")
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

# Create ingredients string and fetch API data if ingredients are selected
ingredients_string = ', '.join(ingredients_list) if ingredients_list else ''

if ingredients_list:
    try:
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        if fruityvice_response.status_code == 200:
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Error: Received status code {fruityvice_response.status_code} from the API.")
    except requests.RequestException as e:
        st.error(f"Error fetching data from Fruityvice API: {e}")

# Button to submit order
time_to_insert = st.button('Submit Order')

if time_to_insert and ingredients_string:
    # Prepare insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    # Execute insert statement
    session.sql(my_insert_stmt).collect()
    st.success(f"Your {name_on_order} is ordered!",
