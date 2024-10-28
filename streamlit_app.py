import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Establish Snowflake session using secrets from Streamlit configuration
def get_snowflake_session():
    try:
        # Use st.secrets["snowflake"] directly for the connection parameters
        connection_parameters = st.secrets["snowflake"]
        return Session.builder.configs(connection_parameters).create()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        st.stop()

# Initialize session
session = get_snowflake_session()

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Query available fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_df['FRUIT_NAME'], max_selections=5)

# Input for name on the order
name_on_order = st.text_input("Enter the name for your smoothie:")

# Insert order if both ingredients and name are provided
if ingredients_list and name_on_order:
    # Prepare ingredients string in a simple comma-separated format
    ingredients_string = ', '.join(ingredients_list)

    # Prepare SQL insert statement
    insert_query = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write("Insert Query:", insert_query)

    # Submit button to insert order
    if st.button('Submit Order'):
        session.sql(insert_query).collect()
        st.success(f"Order for {name_on_order} added with ingredients: {ingredients_string}", icon="✅")
