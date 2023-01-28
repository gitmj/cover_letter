# Import 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import from standard library
import logging
import random
import re

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

st.set_page_config(page_title="Cover letter", page_icon="🤖", layout="wide")

with st.container():
  st.title("Generate Cover letters")
  # TODO: update githbub and add linkedin profile
  st.markdown("This mini-app generates cover letters using OpenAI's GPT-3 based [Davinci model](https://beta.openai.com/docs/models/overview). You can find the code on [GitHub](https://github.com/kinosal/tweet) and the author on [LinkedIn](https://www.linkedin.com/in/manoj-tiwari-17b9213/).")
