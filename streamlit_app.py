# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe  # Pass the list of fruits here
    ,max_selections=5
)

if ingredients_list:
    ingredients_string = ' '
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '


    #st.write(ingredients_string) 

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    #st.write("SQL Statement:", my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    # Insert the order into the database and confirm success
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered under the name "{name_on_order}"! ✅')



# New section to display fruityvice nutrition information
import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
#st.text(fruityvice_response.json())
fv_df = st.dataframe(data=fruityvice_rewponse.jsopn(), use_container_width=True)
