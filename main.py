from dotenv import load_dotenv
import os
import streamlit as st
load_dotenv()
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.llms import GooglePalm
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.chains import RetrievalQA


llm = GooglePalm(google_api_key=os.environ["GOOGLE_PALM_API_KEY"], temperature=0.4) # higher temperature equals more creative, lower temperature equals less creative


instruct_embeddings = HuggingFaceInstructEmbeddings()
vector_db_file="faiss_db_index"
def setup_vector_db():
    loader = CSVLoader(file_path='uwi_dcit_faqs.csv', source_column='prompt')
    data = loader.load()
    vector_database = FAISS.from_documents(documents=data, embedding=instruct_embeddings)
    #retriever = vector_database.as_retriever(score_threshold=0.7)
    vector_database.save_local(vector_db_file)

vector_database = FAISS.load_local(vector_db_file, instruct_embeddings)
retriever = vector_database.as_retriever(score_threshold=0.7)

prompt_template = """Given the following context and a question, generate an answer based on this context only.
In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

CONTEXT: {context}

QUESTION: {question}"""


PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}

retrieval_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    input_key="query",
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs
)
st.title("UWI DCIT CHATBOT 🤖")
btn = st.button("Generate Knowledge base from gathered data.")
if btn:
    setup_vector_db()

question = st.text_input("Question: ")

if question:
 
    response = retrieval_qa_chain(question)

    st.header("Answer")
    st.write(response["result"])
