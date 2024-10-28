import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

def format_ingredients(ingredients_list):
    # Join ingredients into a consistent, comma-separated format with no extra spaces
    return ','.join(ingredient.strip() for ingredient in ingredients_list)

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Establish Snowflake session
session = get_active_session()

# Retrieve available fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_df['FRUIT_NAME'], max_selections=5)

if ingredients_list:
    # Format ingredients consistently
    ingredients_string = format_ingredients(ingredients_list)
    st.write("Formatted Ingredients:", ingredients_string)

    # SQL Insert Statement
    insert_query = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write("Insert Query:", insert_query)

    # Submit button for order insertion
    if st.button('Submit Order'):
        session.sql(insert_query).collect()
        st.success(f"Order for {name_on_order} added with ingredients: {ingredients_string}", icon="✅")
