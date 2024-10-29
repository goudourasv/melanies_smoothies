# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests



# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your current smoothie.
    """
)

cnx = st.connection("snowflake")
session = cnx.session()


name_on_order = st.text_input("Name of Smoothie")
st.write("The name of your smoothie will be: ", name_on_order)


my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)


if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '"""+name_on_order+"""')"""

    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your '+ name_on_order+  ' is ordered!', icon="✅")
