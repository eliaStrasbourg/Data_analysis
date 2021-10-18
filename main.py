import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests
import json
import random

from datetime import datetime as dt


DATA_PATH = './twitchdata-update.csv'

@st.cache
def load_data():
    original_df = pd.read_csv(DATA_PATH)
    df = pd.DataFrame()

    api_token = 'ifivjluh4a3qdjnhqeiqnhtreixvnm'
    client_id = 'zguv1472ecuset2kk12dvgufrn5aa6'
    headers = {
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Client-ID': client_id,
        'Authorization': f'Bearer {api_token}'
    }

    for index, row in original_df.iterrows():
        channel = row['Channel']
        print(channel, ':', index, '/', len(original_df.values))

        try:
            user_res = requests.get(f'https://api.twitch.tv/helix/users?login={channel}', headers=headers)
            id = json.loads(user_res.text)['data'][0]['id']
        except:
            continue
        try:
            channel_res = requests.get(f'https://api.twitch.tv/helix/channels?broadcaster_id={id}', headers=headers)
            channel = json.loads(channel_res.text)['data'][0]['game_name']
        except:
            continue

        new_row_datas = row
        new_row_datas['Category'] = channel
        new_row = pd.Series(new_row_datas)
        df = df.append(new_row)

    df.drop(['Followers gained', 'Views gained', 'Watch time(Minutes)', 'Partnered'], axis=1, inplace=True)
    df = df[(df['Category'] != '') & (df['Channel'] != '') & (df['Language'] != '')]

    not_gaming = ['ASMR', 'Art', 'Chess', 'Codenames', 'Crypto', 'Music', 'OFF', 'Poker', 'Sports', 'UNDEFINED']


    df = df[~(df['Category'].isin(not_gaming))]

    return df



# Layout

st.set_page_config(layout="wide")
input_col, data_col = st.columns([1, 3])


# Data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! (using st.cache)")

categories = data['Category'].unique()
language = data['Language'].unique()



# Input components

selected_categories = []
selected_language = 'English'


with input_col:
    st.header('Inputs')
    with st.expander('Choose streamer categories'):
        for category in categories:
            selected_categories.append(st.checkbox(category))

    selected_language = st.selectbox('Choose a streamer language', tuple(language))



# Data visualization 

filter_categories = []


for i in range(len(selected_categories)):
    if selected_categories[i]:
        filter_categories.append(categories[i])

filtered_data = data[data['Category'].isin(filter_categories) & (data['Language'] == selected_language)]

gaming_groups = filtered_data.groupby('Category').mean().sort_values(by=['Average viewers'], ascending=False).head(10)
gaming_average_viewers = gaming_groups['Average viewers']
gaming_categories = gaming_groups.index.values

with data_col:
    st.header('Data visualization')
    if len(gaming_average_viewers.values) > 0:
        fig, ax = plt.subplots(figsize=(20, 8))

        gaming_average_viewers.plot(kind='bar', title='', ylabel='Average viewers', xlabel='Categories', ax=ax)
        fig.patch.set_facecolor('#0e1117')
        ax.set_title('Average viewers for each gaming categories', fontsize=15, color='white');
        ax.patch.set_facecolor('#0e1117')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        st.dataframe(filtered_data[filtered_data['Category'].isin(categories)].sort_values(by=['Average viewers', 'Followers'], ascending=False))
        st.pyplot(fig)
    else:
        st.text('No data to show')