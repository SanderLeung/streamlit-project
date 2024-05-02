import streamlit as st
import os
from supabase import create_client, Client
from streamlit_supabase_auth import login_form
import pandas as pd
import altair as alt

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title('Protein cost to density visualizer')

session = st.session_state.get('login')
if not session:
    session = login_form(
        url=url,
        apiKey=key,
        providers=["google"],
        )

def get_user():
    return st.session_state.login["user"]

def load_data():
    user_id = get_user()["id"]
    response = supabase.table('groceries').select('name, protein, calories, servings, cost, tags').eq('user_id', user_id).execute()
    return response

if session:
    groceries = load_data()
    st.subheader('Raw data')
    chart_data = pd.DataFrame(groceries.data)
    chart_data['leanness'] = (chart_data['protein']*4/chart_data['calories'])
    chart_data['price_eff'] = (chart_data['protein']*chart_data['servings']/chart_data['cost'])
    st.write(chart_data)

    st.subheader('Scatter plot')
    st.scatter_chart(chart_data, x='leanness', y='price_eff', color='name')

    st.subheader('Bar charts')
    st.bar_chart(chart_data.set_index('name').sort_values(by='leanness', ascending=False), y='leanness')
    st.bar_chart(chart_data.set_index('name').sort_values(by='price_eff', ascending=False), y='price_eff')

    lean = (
        alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('name:N').sort('-y'),
            y='leanness:Q'
        )
    )
    st.altair_chart(lean, use_container_width=True)

    eff = (
        alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('name:N').sort('-y'),
            y='price_eff:Q'
        )
    )
    st.altair_chart(eff, use_container_width=True)