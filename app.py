import json
import urllib
from googleapiclient.discovery import build
from pymongo import MongoClient, server_api
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import mysql

# Function to get channel ID by name
def get_channel_id_by_name(api_key, channel_name):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        q=channel_name,
        type='channel',
        part='id'
    )
    response = request.execute()
    if len(response['items']) == 0:
        return None
    return response['items'][0]['id']['channelId']

# Function to get channel details by ID
def get_channel_details_by_id(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(
        id=channel_id,
        part="snippet,statistics,contentDetails"
    )
    response = request.execute()
    return response['items'][0] if 'items' in response else None


# YouTube API credentials
API_KEY = "AIzaSyBgJ3dn_XKfqtJD8BB_vzW25dX6OF1Xw3U"

# MongoDB credentials
MONGODB_USERNAME = "venkat1585"
MONGODB_PASSWORD = "P@ssw0rd"
MONGODB_HOST = "cluster0.qyp96ey.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"

# MySQL credentials
db_config = {
'MYSQL_HOST' : "localhost",
'MYSQL_USER' : "root",
'MYSQL_PASSWORD' : "P@ssw0rd",
'MYSQL_DATABASE' : "Youtube_database"
}
def connect_mongodb():
    encoded_username = urllib.parse.quote_plus(MONGODB_USERNAME)
    encoded_password = urllib.parse.quote_plus(MONGODB_PASSWORD)
    mongo_uri = f"mongodb://{encoded_username}:{encoded_password}@{MONGODB_HOST}"
    mongodb_client = MongoClient(mongo_uri) 
    return mongodb_client['youtube_data_lake']
st.title("My Youtube Channel Project")

# Initialize or load search history
try:
    with open('search_history.json', 'r') as f:
        search_history = json.load(f)
except Exception:
    search_history = []

# Dropdown for search history
selected_channel = st.selectbox(
    'Select a previous search or type a new one:',
    options=['New Search'] + search_history
)

# Text input for new searches
if selected_channel == 'New Search':
    channel_name = st.text_input('Enter your Channel Name:')
else:
    channel_name = selected_channel

if st.button('Submit') and channel_name:

# Your code for fetching and displaying channel details here
# Save the new search into history
    if channel_name not in search_history:
        search_history.append(channel_name)
        with open('search_history.json', 'w') as f:
            json.dump(search_history, f)
    channel_id = get_channel_id_by_name(API_KEY, channel_name)
    
    if channel_id:
        channel_info = get_channel_details_by_id(API_KEY, channel_id)
    if channel_info:
        channel_name = channel_info['snippet']['title']
        subscriber_count = channel_info['statistics']['subscriberCount']
        total_video_count = channel_info['statistics']['videoCount']
        uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
        thumbnail_url = channel_info['snippet']['thumbnails']['high']['url']
        channel_start_date = channel_info['snippet']['publishedAt']
        # Fetch details of each video
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=100  
        )
        response = request.execute()
        video_details_list = []
        
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            published_date = item['snippet']['publishedAt'] 
            
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            
            # Fetch video statistics
            request = youtube.videos().list(
                part="statistics",
                id=video_id
            )
            video_response = request.execute()
            video_statistics = video_response['items'][0]['statistics']
            
            video_details_list.append({
                'Video ID': video_id,
                'Title': video_title,
                'Likes': video_statistics.get('likeCount', 'N/A'),
                'Dislikes': video_statistics.get('dislikeCount', 'N/A'),
                'Comments': video_statistics.get('commentCount', 'N/A'),
                'published_date': video_statistics.get('published_date', 'N/A')
            })
#df = pd.DataFrame(video_details_list)
    test = {
        "Thumb_nail": thumbnail_url,
        "Channel_name": channel_name,
        "channel_id": channel_id,
        "Subscriber Count": subscriber_count,
        "Total Video Count": total_video_count,
        "Uploads Playlist ID": uploads_playlist_id,
        "Published_date":published_date
    }
# Create DataFrame
    df = pd.DataFrame(video_details_list)
    test = {}
    test = {"Channel_name": channel_name,"channel_id":channel_id,"Subscriber Count":subscriber_count,"Total Video Count":total_video_count,"Uploads Playlist ID":uploads_playlist_id,"Video Details":video_details_list}
    video_titles_plot = [channel_name]
    view_counts_plot = [100, 200, 150, 300]
        
    df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0).astype(int) 
    df_sorted = df.sort_values(by='Likes', ascending=False)
    top_10_videos = df_sorted.head(10)

    def plot_bar_chart(video_titles_plot, view_counts_plot):
        plt.figure(figsize=(10, 6))
        plt.barh(video_titles_plot, view_counts_plot, color='skyblue')
        plt.xlabel('View Counts')
        plt.ylabel('Video Titles')
        plt.title('Total Videos vs Views')
        st.pyplot(plt)
        st.title("YouTube Video Analytics")
        plot_bar_chart(video_titles_plot, view_counts_plot)
    
    st.subheader("Channel Details")
    st.markdown(
    f"<div style='text-align: center'><img src='{thumbnail_url}' width='200'><br>{channel_name}'s Thumbnail</div>",
    unsafe_allow_html=True,
        )
    st.write(f"**Channel Name:** {test['Channel_name']}")
    st.write(f"**Channel ID:** {test['channel_id']}")
    st.write(f"**Subscriber Count:** {test['Subscriber Count']}")
    st.write(f"**Total Video Count:** {test['Total Video Count']}")
    st.write(f"**Uploads Playlist ID:** {test['Uploads Playlist ID']}")
    st.write(f"**Channel Start Date:** {test.get('Published_date', 'Not available')}") 
    st.subheader("Video Details")
    st.write(df)    
    #df = pd.DataFrame(video_details_list)
    
# Convert the 'Likes' column to integers, replacing 'N/A' with 0
    df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0).astype(int)
    
    def data_migrate(migrate):
        # create sql connection
        conn = mysql.connect("Youtube.db")
        cursor = conn.cursor()
        try:
            conn = mysql.connector.connect(**db_config)
            print("Connection established")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        # create tables
        channel_table = '''
                CREATE TABLE IF NOT EXISTS channel (
                channel_id VARCHAR(255),
                channel_Name VARCHAR(255) PRIMARY KEY,
                channel_Description TEXT,
                subscriber_Count INT,
                view_Count BIGINT,
                video_Count INT,
                upload_id VARCHAR(255),
                published_Date DATE)'''
        
        video_table = '''
                CREATE TABLE IF NOT EXISTS video (
                Channel_id VARCHAR(255),
                Video_id VARCHAR(255) PRIMARY KEY,
                Video_title TEXT,
                Video_Duration VARCHAR(255),
                Video_Description TEXT,
                Video_Published_Date DATE,
                Video_View_Count BIGINT,
                Video_Like_Count INT,
                Video_Comment_Count INT
            )
        '''
        comment_table = '''
                CREATE TABLE IF NOT EXISTS comment (
                comment_id VARCHAR(255),
                video_id VARCHAR(255),
                comment_Author_Name VARCHAR(255),
                comment_Text TEXT,
                comment_Published_Date DATE,
                comment_Like_Count INT,
                comment_Reply_Count INT,
                FOREIGN KEY (video_id) REFERENCES video(Video_Id)
                )'''

        cursor.execute(channel_table)
        cursor.execute(video_table)
        cursor.execute(comment_table)
        
    
# Plotting bar chart for 'Likes' against 'Title'
    st.subheader("Bar Chart: Video Likes")
    st.bar_chart(df.set_index('Title')['Likes'])
    st.subheader("Bar Chart: Top 10 Most Popular Videos Based on Likes")
    st.bar_chart(top_10_videos.set_index('Title')['Likes'])
        
# MongoDB Connection
    username = "venkat1585"
    password = "P@ssw0rd"
    encoded_username = urllib.parse.quote_plus(username)
    encoded_password = urllib.parse.quote_plus(password)
    mongo_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.qyp96ey.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"
    ds = pd.DataFrame(video_details_list)
    
    
#client = MongoClient(uri)

    client = MongoClient(mongo_uri, server_api=server_api.ServerApi('1'), tz_aware=False, connect=True, tlsInsecure=True)
    client.admin.command('ping')
    
    try:
        
        st.write("Successfully connected to MongoDB!")
        db = client['Youtube_database']
        collection = db['channel_de']
        collection_insert_status = collection.insert_one(test)
        st.write("Data inserted into MongoDB!")
        st.write("Data transferred from MongoDB to MySQL Database.")
    except Exception as e:
        st.write(f"Connection to MongoDB failed: {e}")
        
    else:
        print("No channel found with the given name.")





