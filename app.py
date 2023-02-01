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

max_resume_page = 2

max_context_size = 4096

def read_resume(file):
    resume = ""
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        if (len(pages) > max_resume_page):
          st.session_state.text_error = "Resume too long." + " Max supported page: " + str(max_resume_page)
          logging.info(f"File name: {file} too big\n")
          st.error(st.session_state.text_error)
          return ""
        for p in pages:
            resume = resume + p.extract_text()
    logging.info("Number of words in resume: " + str(len(resume.split())))
    return resume

def resume_upload_callback():
  if st.session_state['resume_uploader'] is not None:
    st.session_state["resume_ctr"] += 1
    st.session_state["resume_text"] = read_resume(st.session_state['resume_uploader'])

def job_description_callback():
  if st.session_state["job_description_input"] is not None:
    logging.info("Number of words in job description: " +
      str(len(st.session_state.job_description_input.split())))

def prompt_tunning(resume_text: str, job_description: str, letter_size: int):
  prompt = "Write a cover letter with following resume and job description: "
  prompt = prompt + resume_text + job_description
  num_prompt_words = len(prompt.split())
  if (num_prompt_words + letter_size > max_context_size):
    err_str = f"Prompt + letter size are too big to handle: {num_prompt_words} and {letter_size}"
    st.session_state.text_error = err_str
    logging.info(err_str)
    st.error(err_str)
    return None

  logging.info("Number of words in prompt: " + str(num_prompt_words))
  return prompt

def generate_letter(resume_text: str, job_description: str):
  if st.session_state.n_requests >= 5:
    st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another letter."
    logging.info(f"Session request limit reached: {st.session_state.n_requests}")
    st.session_state.n_requests = 1
    return

  if not resume_text:
    err_str = "Resume is empty"
    logging.info(err_str)
    st.error(err_str)
    return

  if not job_description:
    err_str = "Job description is empty"
    logging.info(err_str)
    st.error(err_str)
    return

  #with text_spinner_placeholder:
  with st.spinner("Please wait while your letter is being generated..."):
    prompt = prompt_tunning(resume_text, job_description, st.session_state.letter_size)
    if not prompt:
      logging.info (f"Couldn't configure prompt successfully")
      return

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
  st.session_state.letter_size = 200 # small

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
    st.markdown("No account signup, Just provide your resume and job description to get personalized cover letter.")
    st.markdown("Generated via OpenAI's ChatGPT [Davinci model](https://beta.openai.com/docs/models/overview).")
    st.markdown("Author's [LinkedIn](https://www.linkedin.com/in/manoj-tiwari-17b9213/). Feel free to connect!")
    resume_file = st.file_uploader("Choose your resume .pdf file", type="pdf",
      on_change=resume_upload_callback, key="resume_uploader")

    st.text_input(label="Job Description", placeholder="Enter job description",
      on_change=job_description_callback,
      key="job_description_input")

    letter_size = st.radio(
    "Please select letter size (in number of words)",
    ('Small (200)', 'Medium (400)', 'Large (600)'), index = 1)
    if letter_size == "Small (200)":
      st.session_state.letter_size = 200
    elif letter_size == "Medium (400)":
      st.session_state.letter_size = 400
    else:
      st.session_state.letter_size = 600

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    st.button(
        label="Generate cover letter",
        type="primary",
        on_click=generate_letter,
        args=(st.session_state["resume_text"], st.session_state["job_description_input"]),
        )

  with col2:
    components.html(
    f'<script src="https://donorbox.org/widget.js" paypalExpress="false"></script><iframe src="https://donorbox.org/embed/effective-cover-letters?default_interval=o&amount=1" name="donorbox" allowpaymentrequest="allowpaymentrequest" seamless="seamless" frameborder="0" scrolling="auto" height="900px" width="100%" style="max-width: 500px; min-width: 250px; max-height:none!important"></iframe>',
    height=650,
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

contact_form = """
<form action="https://formsubmit.co/manoj41@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email"" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""
st.header(":mailbox: Get in touch with me!")
st.markdown(contact_form, unsafe_allow_html=True) 

# Use local css file
def local_css(file_name):
  with open(file_name) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")
