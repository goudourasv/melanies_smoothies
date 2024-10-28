import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark.types import StringType

# Ensure only one active session
try:
    session = get_active_session()
except:
    st.error("No active session found. Please ensure your Snowflake connection is properly configured.")
    st.stop()

# Register the UDF using `session.udf.register`
def format_ingredients(ingredients_list: str) -> str:
    # Split and format ingredients consistently
    ingredients = ingredients_list.split(",")
    return ','.join(ingredient.strip() for ingredient in ingredients)

# Register UDF with explicit session
format_ingredients_udf = session.udf.register(
    func=format_ingredients,
    return_type=StringType(),
    input_types=[StringType()],
    name="UTIL_DB.PUBLIC.FORMAT_INGREDIENTS_UDF",  # Use a unique name
    is_permanent=False,  # Set to True if you want it stored permanently
    replace=True,  # Replace if it already exists
    session=session
)

# App title and description
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Query available fruit options
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_df['FRUIT_NAME'], max_selections=5)

# Insert order with formatted ingredients
if ingredients_list:
    # Apply UDF to format ingredients
    ingredients_string = ','.join(ingredients_list)
    formatted_ingredients = format_ingredients(ingredients_string)

    # Prepare SQL statement
    insert_query = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{formatted_ingredients}', 'Test_Order')
    """
    st.write("Insert Query:", insert_query)

    # Submit button to insert order
    if st.button('Submit Order'):
        session.sql(insert_query).collect()
        st.success(f"Order added with ingredients: {formatted_ingredients}", icon="✅")
