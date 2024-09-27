import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from io import StringIO
import re
import csv
import boto3
import json
import seaborn as sns
import matplotlib.pyplot as plt
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
from dotenv import load_dotenv

load_dotenv()

def clean_response(text):
    cleaned_text = text.replace('*','').replace('|','').strip()
    lines = cleaned_text.split('\n')
    lines = [line for line in lines if line.strip() and not re.match(r'^[-\s]+$', line)]
    data = [re.split(r'\s{2,}', line.strip()) for line in lines]
    return data

def convert_response_to_csv(text):
    data = clean_response(text)
    if not data or len(data) < 2:
        st.write("Error: No valid data found to Generate CSV")
        return None
    max_columns = len(data[0])
    cleaned_data = []
    for row in data:
        if len(row) < max_columns:
            row += [''] * (max_columns - len(row))
        elif len(row) > max_columns:
            row = row[:max_columns]
        cleaned_data.append(row)
    df = pd.DataFrame(cleaned_data[1:], columns=cleaned_data[0])
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer

st.set_page_config("ESG Data and Reporting", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #f0f0f0;
        background-size: cover;
        background-position: center;
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
    }
    title {
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    .stButton>button {
        background-color: #4CAF50;  /* Green */
        color: white;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Select Options")
option = st.sidebar.selectbox("Choose Options", ("ESG Data Generation", "ESG Data Duplication"))

#if st.sidebar.button("Submit"):
    #st.write(f"You selected {option}")

if option == "ESG Data Generation":
    st.title("ESG Data and Reporting :leaves: :fog:")
    sample = st.selectbox("If you have sample data", ("Yes", "No"))
    if sample == "Yes":
        file1 = st.file_uploader("Please upload the file", type=["csv"])
        if file1 is not None:
            df = pd.read_csv(file1)
            st.dataframe(df)
            csv_text = df.to_csv(index=False)
            #st.write(df)
            #st.text_area("Table form", csv_text)
           
            num = st.slider("Enter the number of rows to be generated", step=1)
            col1 = st.selectbox("Select the first column for comparison", df.columns)
            col2 = st.selectbox("Select the second column for comparison", df.columns)
            #row1 = st.number_input("Enter the number of rows", step=1, min_value=0, value=1)
            #coloumn1 = st.number_input("Enter the coloumns", step=1, min_value=0, value=1)
            submit1 = st.button("Generate Data")
            #st.write(num)
            template = f'''I want you to act as a ESG data Generator and to below mentioned steps :
                        1) Analyze the CSV file given by me first and identify the company and what type of data is there.
                        2) After analyzing the data generate the new data such that the new data generated should be accurate and within the scope of data provided in CSV file.
                        3) The new data generated should be of {num} rows only make sure it should not be more or less.
                        4) And add the new data end the end of given CSV file.
                        5) Ouput only the final table containing both CSV file and newly generated rows in a tabular form not the analyzing and new data generation part..
                        The CSV file is this : {csv_text}
                        '''
            #st.write(template)
        
            if submit1:
                metadata = SingleTableMetadata()
                metadata.detect_from_dataframe(data=df)
                for column_name in metadata.columns.keys():
                    if metadata.columns[column_name].get('sdtype') in ['id', 'unique']:
                        metadata.update_column(column_name=column_name, sdtype='categorical')
                    else:
                        metadata.update_column(column_name=column_name, sdtype='categorical')
                metadata.primary_key = None
                #synthesizer = CTGANSynthesizer(metadata)
                synthesizer = GaussianCopulaSynthesizer(metadata)
                bootstrapped_df = pd.concat([df] * 8, ignore_index=True)
                for column in bootstrapped_df.select_dtypes(include=[np.float32]).columns:
                    bootstrapped_df[column] = bootstrapped_df[column] + np.random.normal(0,0.1,bootstrapped_df[column].shape)
                synthesizer.fit(bootstrapped_df)
                synthetic_data = synthesizer.sample(num_rows=num)
                st.dataframe(synthetic_data)
                fig , ax = plt.subplots(1,2, figsize=(14,6))
                sns.scatterplot(x=df[col1], y=df[col2], ax=ax[0], color="blue", label="Real Data")
                ax[0].set_title(f"Real Data: {col1} vs {col2}")
                sns.scatterplot(x=synthetic_data[col1], y=synthetic_data[col2], ax=ax[1], color="green", label="Synthetic Data")
                ax[1].set_title(f"Synthetic Data: {col1} vs {col2}")
                st.pyplot(fig)
                final_df = pd.concat([df, synthetic_data], ignore_index=True)
                st.write("Updated CSV with synthetic data")
                st.dataframe(final_df)
                csv = final_df.to_csv(index=False)
                st.download_button("Download Updated CSV with synthetic data", csv, "Updated_file.csv", "text/csv")
                #response1 = get_yes_gemini_response(template)
                #st.write(response1)
                #csv_buffer = convert_response_to_csv(response1)
                #if csv_buffer:
                    #csv_data = csv_buffer.getvalue().encode('utf-8')
                    #st.download_button("Download CSV", csv_data, "Generated_data.csv", "text/csv")
                
    elif sample == "No":
        tech = st.selectbox("Choose the Industry", ("Vehicle Manufacturing", "Finance", "Healthcare", "Technology", "Other"))
        data = st.text_input("What type of data to be generated: ESG Scope 1, ESG Scope 2, ESG Scope 3", placeholder="ESG")
        company = st.text_input("For what type of company you want data to be Generated", placeholder="Any Company")
        country = st.text_input("Enter the country for which you want data to be Generated", placeholder="India")
        location = st.text_input("Enter the location for which you want data to be Generated", placeholder="Banglore")
        year = st.text_input("Enter the yearfor which you want data to be Generated", placeholder="2023")
        rows = st.number_input("Enter the number of rows", step=1, min_value=0, value=1)
        coloumns = st.number_input("Enter the number of Columns", step=1,min_value=0, value=1)
        submit = st.button("Generate data")
        prompt_template = f'''Act as an ESG Data Generator and generate the data based on below given details.
                        1) Industry type for which data should be generated : {tech}
                        2) Company for which data should be generated : {company}
                        3) Country for which data should be generated : {country}
                        4) Location for which data should be generated : {location}
                        5) Year : {year}
                        6) Type of data to be generated : {data}
                        7) Number of rows to be generated : {rows}    
                        8) Number of coloumns to be generated : {coloumns}
                        Just generate tabular form data only for the details given dont't provide any text.
                        And generate data on the basis of number of rows and columns i asked and also generate actual data not estimated one.
                        I know the data generated is hypothetical so i dont want you to mention that in output.
                        '''

        if submit:
            #response = get_gemini_response(prompt_template)
            #response = get_amazon_bedrock(prompt_template)
            client = boto3.client("bedrock-runtime", 
                                  region_name="us-east-1",
                                  aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
                                  aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                                  )
            model_id = "amazon.titan-text-premier-v1:0"
            native_request = {
                "inputText": prompt_template,
                "textGenerationConfig": {
                    "maxTokenCount": 1024,
                    "temperature": 0.1,},
                    }
            request = json.dumps(native_request)
            response = client.invoke_model(modelId=model_id, body=request)
            model_response = json.loads(response["body"].read())
            response_text = model_response["results"][0]["outputText"]
            st.write(response_text)
            #print(type(response))
            #st.write(response)
            csv_buffer = convert_response_to_csv(response_text)
            if csv_buffer:
                csv_data = csv_buffer.getvalue().encode('utf-8')
                st.download_button("Download CSV", csv_data, "Generated_data.csv", "text/csv")

elif option == "ESG Data Duplication":
    st.title("ESG Data and Reporting :leaves: :fog:")
    file = st.file_uploader("Please upload the file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        st.dataframe(df)
        num_rows = len(df)
        #st.text_input("Enter the maximum range")
        #st.text_input("Enter the minimum range")
        total_rows_to_duplicate = st.slider("Select the rows to be duplicated", step=1)
        duplicated_rows = []
        while len(duplicated_rows) < total_rows_to_duplicate:
            for i in range(num_rows):
                duplicated_rows.append(df.iloc[i])
                if len(duplicated_rows) >= total_rows_to_duplicate:
                    break
        duplicated_df = pd.DataFrame(duplicated_rows)
        df_extended = pd.concat([df,duplicated_df], ignore_index=True)
        st.write("Updated CSV")
        st.dataframe(df_extended)
        csv = df_extended.to_csv(index=False)
        st.download_button("Download Updated CSV", csv, "Updated_file.csv", "text/csv")

