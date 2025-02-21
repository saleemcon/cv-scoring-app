import io
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, tool

_ = load_dotenv(find_dotenv())

########################### Model Definition ##################################################33
# Define Model
model = ChatOpenAI(model_name="gpt-4-1106-preview",
                   temperature=0.3,
                   presence_penalty=0.5,  # Adjust as needed
                   frequency_penalty=0.5,  # Adjust as needed
                   top_p=0.9,  # Adjust as needed
                   seed=12345)  # Set a specific seed for random number generation########################### Call Function #####################################################

@tool
def create_dataframe(Sequence_Number, Applicant_Name, Strength, Weakness, Score):
    """
    Creates a Data frame from resume details.

    Parameters:
    - Sequence_Number (List): Sequence
    - Applicant_name (list): Names of applicant.
    - Strength (list): Strength points.
    - Weakness (list): Weakness points.
    - Score (list): mark from 10.

    Returns:
    - DataFrame: DataFrame with specified columns. Missing data is filled with None.

    Note:
    - Input lists are extended with None to equalize their lengths.
    """

    # Ensure that both lists have the same length
    max_length = max(len(Sequence_Number), len(Applicant_Name), len(Strength), len(Weakness), len(Score))

    # Extend each list to the maximum length by filling with None
    Sequence_Number.extend([None] * (max_length - len(Sequence_Number)))
    Applicant_Name.extend([None] * (max_length - len(Applicant_Name)))
    Strength.extend([None] * (max_length - len(Strength)))
    Weakness.extend([None] * (max_length - len(Weakness)))
    Score.extend([None] * (max_length - len(Score)))

    # Create the DataFrame
    data = {
        'CV Number': Sequence_Number,
        'Applicant Name': Applicant_Name,
        'Strength': Strength,
        'Weakness': Weakness,
        'Score': Score
    }
    df = pd.DataFrame(data)
    file_path = 'files/cv_evaluation.xlsx'
    df.to_excel(file_path, index=False)

    return df

st.markdown("<h1 style='color: #007bff;'>Applicants Evaluation</h1>", unsafe_allow_html=True)

st.markdown("""
    <style>
    label {
        color: #007bff !important;
    }
    </style>
    """, unsafe_allow_html=True)
################################Upload Job Description#########################################
uploaded_JobDescription = st.file_uploader("Choose a Job Description file", type="pdf")
err=""
JobDescText=""
if uploaded_JobDescription:
    try:
      file_bytes = io.BytesIO(uploaded_JobDescription.getvalue())
      JobDescReader = PdfReader(file_bytes)
      for i, page in enumerate(JobDescReader.pages):
           text2 = page.extract_text()
           if text2:
              JobDescText += text2
      if not JobDescText:
                st.error(f"Could not read text from '{uploaded_JobDescription.name}'. Please check the file and try again.")
                err = "1"

    except Exception as e:
            st.error(f"Could not read text from '{uploaded_JobDescription.name}'. Please check the file and try again.")
            err = "1"
################################Upoad Resumes #########################################
uploaded_files = st.file_uploader("Choose a CV file", type="pdf", accept_multiple_files=True)

raw_text = ""
TextArray=[]
if uploaded_files:
    # Read and process the uploaded PDF file
       for uploaded_file in uploaded_files:
          try:
              file_bytes = io.BytesIO(uploaded_file.getvalue())
              reader = PdfReader(file_bytes)
              raw_text=""
              for i, page in enumerate(reader.pages):
                  text = page.extract_text()
                  if text:
                     raw_text += text

              if not raw_text:
                   st.error(f"Could not read text from '{uploaded_file.name}'. Please check the file and try again.")
                   err = "1"
              else:
                   TextArray.append(raw_text)
          except Exception as e:
                st.error(f"Could not read text from '{uploaded_file.name}'. Please check the file and try again.")
                err = "1"


############################### Action #######################################
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
    }
    </style>    
    """, unsafe_allow_html=True)

if st.button("Evaluate") :
   if not err and TextArray and JobDescText:
          tools = [create_dataframe]

          agent = initialize_agent(tools, model, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

          res = agent.run(f"For each resume, perform the following tasks:\n\n1. Extract the Sequence Number.\n\n2. Identify the Applicant's Name.\n\n3. Highlight the Strength Points relevant to the job description.\n\n4. Point out any Weakness Points with respect to the job requirements.\n\n5. Assign a Score out of 10, based on how well the resume matches the job description.\n\nJob Description: {JobDescText}\n\nResumes Text: {TextArray}")
          st.write(res)

   else:
           st.warning("Check Uploaded CV's and Job Description files")






