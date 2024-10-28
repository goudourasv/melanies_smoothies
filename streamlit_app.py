import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, udf
from snowflake.snowpark.types import StringType

# Ensure only one active session is retrieved
session = get_active_session()

# Define a UDF and register it with the session
@udf(name="format_ingredients_udf", is_permanent=False, session=session)
def format_ingredients(ingredients_list: str) -> str:
    # Function to format ingredients in a consistent way
    ingredients = ingredients_list.split(",")
    return ','.join(ingredient.strip() for ingredient in ingredients)

# Use session throughout the app for consistency
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Use the UDF in your query, if needed
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Display DataFrame for debugging
st.write("Available fruits:", fruit_df)

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_df['FRUIT_NAME'], max_selections=5)

# Use the UDF explicitly in any SQL statements
if ingredients_list:
    formatted_ingredients = format_ingredients(','.join(ingredients_list))  # Apply formatting directly

    # Insert order using the formatted ingredients
    insert_query = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{formatted_ingredients}', 'Test_Order')
    """
    st.write("Insert Query:", insert_query)

    if st.button('Submit Order'):
        session.sql(insert_query).collect()
        st.success(f"Order added with ingredients: {formatted_ingredients}", icon="✅")
