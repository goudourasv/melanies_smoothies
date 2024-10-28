# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark DataFrame to a Pandas DataFrame for easy lookups
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],  # Pass the list of fruits here
    max_selections=5
)

if ingredients_list:
    # Concatenate chosen ingredients into a single string
    ingredients_string = ' '.join(ingredients_list)

    # Loop through selected fruits to fetch nutrition information
    for fruit_chosen in ingredients_list:
        # Find the corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # Display nutrition information using the Fruityvice API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        
        # Check if the request was successful
        if fruityvice_response.status_code == 200:
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}.")

    # SQL Insert Statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    # Insert the order into the database and confirm success
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered under the name "{name_on_order}"! ✅')
