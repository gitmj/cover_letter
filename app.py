# Import 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import from standard library
import logging
import random
import re
import pdfplumber # PyPDF2
from io import StringIO

# Import openai module 
import openai_wrapper

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

st.set_page_config(page_title="Cover letter", page_icon="🤖", layout="wide")

max_resume_page = 3

def read_resume(file):
    resume = ""
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        if (len(pages) > max_resume_page):
          st.session_state.text_error = "Resume too long." + " Max supported page: " + str(max_resume_page)
          logging.info(f"File name: {file_name} too big\n")
          return ""
        for p in pages:
            resume = resume + p.extract_text()
    return resume

def resume_upload_callback():
  if st.session_state['resume_uploader'] is not None:
    st.session_state["resume_ctr"] += 1
    st.session_state["resume_text"] = read_resume(st.session_state['resume_uploader'])

def job_description_callback():
  if st.session_state["job_description_input"] is not None:
    logging.info("job callback: " + st.session_state["job_description_input"])


def generate_letter(resume_text: str, job_description: str):
  if st.session_state.n_requests >= 5:
    st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another letter."
    logging.info(f"Session request limit reached: {st.session_state.n_requests}")
    st.session_state.n_requests = 1
    return

  logging.info(resume_text)
  logging.info(job_description)
  #with text_spinner_placeholder:
  with st.spinner("Please wait while your letter is being generated..."):
    prompt = (
      f"Write a cover letter with following resume and job description: "
      f"Resume: {resume_text} and job description: {job_description} \n\n"
      )

    openai = openai_wrapper.Openai()
    flagged = openai.moderate(prompt)
    # cleanup previous errors
    if flagged:
      st.session_state.text_error = "Input flagged as inappropriate."
      return
    else:
      st.session_state.text_error = ""
      st.session_state.n_requests += 1

      response = openai.complete(prompt, 0, st.session_state.letter_size)
      st.session_state.cover_letter = response[0]
      st.session_state.total_tokens_used = st.session_state.total_tokens_used + response[1] 

      logging.info (f"Successfully generated cover letter")

  return

# Setup session state
if "resume_text" not in st.session_state:
  st.session_state.resume_text = ""

if "job_description_input" not in st.session_state:
  st.session_state.job_description_input = ""

if "cover_letter" not in st.session_state:
  st.session_state.cover_letter = ""

if "letter_size" not in st.session_state:
  st.session_state.letter_size = 100 # small

if "resume_ctr" not in st.session_state:
  st.session_state.resume_ctr = 0

if "n_requests" not in st.session_state:
  st.session_state.n_requests = 0

if "total_tokens_used" not in st.session_state:
  st.session_state.total_tokens_used = 0

if "text_error" not in st.session_state:
  st.session_state.text_error = ""

# Render main page
with st.container():
  col1, col2 = st.columns(2)
  with col1:
    title = "Personalized Cover Letter!!"
    st.title(title)
    st.markdown("No account signup, Just provide your resume and job description and get custom cover letter.")
    st.markdown("Generated via OpenAI's ChatGPT [Davinci model](https://beta.openai.com/docs/models/overview).")
    st.markdown("Author's [LinkedIn](https://www.linkedin.com/in/manoj-tiwari-17b9213/). Feel free to connect!")
    resume_file = st.file_uploader("Choose your resume .pdf file", type="pdf",
      on_change=resume_upload_callback, key="resume_uploader")

    st.text_input(label="Job Description", placeholder="Enter job description",
      on_change=job_description_callback,
      key="job_description_input")

    st.button(
        label="Generate cover letter",
        type="primary",
        on_click=generate_letter,
        args=(st.session_state["resume_text"], st.session_state["job_description_input"]),
        )

    letter_size = st.radio(
    "Please select letter size (in number of words)",
    ('Small (100)', 'Medium (200)', 'Large (300)'))
    if letter_size == "Small":
      st.session_state.letter_size = 100
    elif letter_size == "Medium":
      st.session_state.letter_size = 200
    else:
      st.session_state.letter_size = 300

  with col2:
    components.html(
    f'<script src="https://donorbox.org/widget.js" paypalExpress="false"></script><iframe src="https://donorbox.org/embed/effective-cover-letters" name="donorbox" allowpaymentrequest="allowpaymentrequest" seamless="seamless" frameborder="0" scrolling="yes" height="500px" width="100%" style="max-width: 500px; min-width: 250px; max-height:none!important"></iframe>',
    height=550,
    )
    
  #text_spinner_placeholder = st.empty()
  if st.session_state.text_error:
      st.error(st.session_state.text_error)

  # if st.session_state.cover_letter:
  st.markdown("""---""")
  total_cost = str((st.session_state.total_tokens_used / 1000) * 0.02)
  # make it red & bold
  total_cost = f"**:red[${total_cost}]**"
  st.markdown("Total cost incurred: " + total_cost +
    " (Please support the service if you like your cover letter!!)")

  st.text_area(label="Cover Letter", value=st.session_state.cover_letter, height=500)
