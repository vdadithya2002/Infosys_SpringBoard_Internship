import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="QueryTube AI", layout="wide")

st.markdown("""
<style>
.search-box {
    width: 60%;
    padding: 12px;
    border-radius: 25px;
    border: 1px solid #ccc;
}
.video-card {
    background-color: #181818;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:red;'>▶ QueryTube AI</h1>", unsafe_allow_html=True)

query = st.text_input("", placeholder="Search", key="search")

if query:
    res = requests.get(f"{API_BASE}/search", params={"query": query})
    data = res.json()

    for video in data.get("results", []):
        st.markdown(f"""
        <div class="video-card">
        <h4>{video['title']}</h4>
        <p>Channel: {video['channel_name']}</p>
        <p>Similarity: {video['similarity']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Summarize", key=video["video_id"]):
            sum_res = requests.get(f"{API_BASE}/summarize", params={"video_id": video["video_id"]})
            st.session_state["summary"] = sum_res.json()["summary"]

if "summary" in st.session_state:
    st.subheader("📄 Video Summary")
    st.write(st.session_state["summary"])
