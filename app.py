import streamlit as st
import pandas as pd
import os
from github import Github


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

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(repo_name)

# ---------- 示例数据 ----------
with open("week_5_generation/Response_by_jinaai_jina-embeddings-v3.md", "r") as f:
    examples = f.read().split("\n\n---\n\n")

examples = examples[:5]
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
            "comment": comment
        }
        for dim in dimensions:
            result[f"{dim}_score"] = scores[dim]

        # 写入 CSV 文件
        df = pd.DataFrame([result])
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(DATA_FILE, index=False)

        st.success("🎉 all ratings submitted")

        # 进入下一条
        if st.session_state.index < len(examples) - 1:
            st.session_state.index += 1
            st.rerun()
        else:
            st.markdown("### 🏁 all the queries done! Thanks for ")
            with open(DATA_FILE, "rb") as f:
                content = f.read()

            # 3. 检查文件是否存在于 GitHub 仓库
            try:
                contents = repo.get_contents(target_path)
                # 4. 如果存在，更新文件
                repo.update_file(
                    path=target_path,
                    message=f"Update {DATA_FILE} via Streamlit",
                    content=content,
                    sha=contents.sha
                )
                st.success(f"✅ Updated {DATA_FILE} on GitHub.")
            except:
                # 5. 如果不存在，创建新文件
                repo.create_file(
                    path=target_path,
                    message=f"Create {DATA_FILE} via Streamlit",
                    content=content
                )
                st.success(f"✅ Created {DATA_FILE} on GitHub.")
            
            

# ---------- 显示进度 ----------
st.markdown(f"📊 Current progress:{st.session_state.index + 1} / {len(examples)}")


