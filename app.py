import streamlit as st
import requests

st.title("MoodMate 🎵")

text = st.text_input("Enter your mood")

if st.button("Get Songs"):
    res = requests.post(
        "http://127.0.0.1:8000/recommend",
        params={"text": text}
    )

    data = res.json()

    st.write("### Emotion:", data["emotion"])

    st.write("### 🎧 Recommended Songs:")

    for song in data["songs"]:
        st.write(f"🎵 {song['song_name']} - {song['artist']}")