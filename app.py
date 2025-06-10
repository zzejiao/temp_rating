import streamlit as st
import pandas as pd
import os
# from github import Github
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .main {
            padding-left: 80px !important;
            padding-right: 80px !important;
        }
    </style>
""", unsafe_allow_html=True)


# ---------- 配置 ----------
DATA_FILE = "Task2_jinaai_jina-embeddings-v3.csv"  # 保存评分的CSV文件路径
repo_name = "zzejiao/temp_rating"
target_path = DATA_FILE

# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# g = Github(GITHUB_TOKEN)
# repo = g.get_repo(repo_name)

# ---------- Google Sheets Configuration ----------
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load credentials from your service account file, use Streamlit secrets
credentials = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
}

credentials = Credentials.from_service_account_info(credentials, scopes=SCOPES)


# Create a Google Sheets client
gc = gspread.authorize(credentials)

# Open your Google Sheet by its title or URL
# Replace 'Your Sheet Name' with your actual sheet name or use sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ztIBidaWHXKeKuNX6PDvS6RE9i_F0KL6jF_fbhYZP7c/edit?gid=179949384#gid=179949384"  # You'll need to replace this
worksheet = gc.open_by_url(SHEET_URL).sheet1

# ---------- 示例数据 ----------
with open("week_5_generation/Response_by_jinaai_jina-embeddings-v3.md", "r") as f:
    examples = f.read().split("\n\n---\n\n")

examples = examples[:-1]
# ---------- 当前任务 ----------
col1, col2 = st.columns([2, 3])

with col1:

    if "index" not in st.session_state:
        st.session_state.index = 0

    example = examples[st.session_state.index]
    st.markdown(f"{example}")

# ---------- 多维度打分 ----------
with col2:
    
    st.markdown("""
                | **Criterion** | **Score 1** | **Score 2** | **Score 3** | **Score 4** | **Score 5** |
|---------------|-------------|-------------|-------------|-------------|-------------|
| **Factuality / Accuracy** | Does not answer the question or answers a different one entirely. | Partially answers the question, with noticeable gaps or misalignment with truths. | Generally answers the question, but with minor misalignment. | Well-aligned with the guideline truths and clearly addresses the question. | Perfectly aligned with the intended question and purpose. |
| **Completeness** | Misses key information or keywords entirely. | Includes some key points but lacks logical flow or completeness. | Covers most key infos with some minor gaps or weak structure. | Includes all important elements, mostly well organized. | Fully complete with all required key infos and logical structure. |
| **Safe and Ethical** | Contains potentially offensive, unethical, or harmful content. | May contain minor ethical or appropriateness concerns. | Mostly appropriate; no major ethical concerns. | Ethically sound and inoffensive. | Completely safe, ethical, and professional. |
| **Clinical Applicability / Generalization / Practicality** | Not applicable or misleading in most real-world clinical cases. | Limited applicability or clarity in clinical practice. | Reasonably generalizable, but may require interpretation. | Generally applicable and practical in clinical settings. | Highly generalizable, specific, and actionable for clinicians. |

""")

    dimensions = ["Factuality", "Completeness", "Safety", "Clnical Applicability"]
    scores = {}

    for dim in dimensions:
        scores[dim] = st.radio(f"**{dim}** ", [1, 2, 3, 4, 5], horizontal=True, key=dim)

    # ---------- 评论 ----------
    comment = st.text_area("💬 Comment）")

    # ---------- 提交评分 ----------
    if st.button("✅ Submit Rating"):
        result = {
            "id": st.session_state.index + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comment": comment
        }
        for dim in dimensions:
            result[f"{dim}_score"] = scores[dim]

        # Write to Google Sheet
        try:
            # Get all existing values
            existing_values = worksheet.get_all_values()
            
            # If sheet is empty, write headers first
            if not existing_values:
                headers = list(result.keys())
                worksheet.append_row(headers)
            
            # Append the new row
            worksheet.append_row(list(result.values()))
            
            st.success("This Rating is submitted to Google Sheet!")
        except Exception as e:
            st.error(f"Failed to write to Google Sheet: {str(e)}")

            
            

# ---------- 显示进度 ----------
st.markdown(f"📊 Current progress:{st.session_state.index + 1} / {len(examples)}")


