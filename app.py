import streamlit as st
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@st.cache_resource
def get_llm():
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama3-8b-8192",
        temperature=0.1
    )

def parse_jd(jd_text):
    """Parse Job Description into structured JSON"""
    llm = get_llm()
    
    prompt = PromptTemplate.from_template("""
    Analyze this job description and extract in VALID JSON format only (no extra text):
    
    {{
        "role": "Job title",
        "experience_level": "Fresher|Junior|Mid|Senior",
        "technical_skills": ["Python", "React", "Docker"],
        "soft_skills": ["leadership", "communication"],
        "responsibilities": ["Build features", "Code review"],
        "tools": ["AWS", "Git", "Jira"],
        "difficulty": "easy|medium|hard"
    }}
    
    Job Description:
    {jd_text}
    
    Respond with ONLY valid JSON:
    """)
    
    try:
        response = llm.invoke(prompt.format(jd_text=jd_text))
        # Clean response and parse JSON
        json_str = response.content.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("```")[1]
        parsed = json.loads(json_str)
        return parsed
    except:
        # Fallback structure
        return {
            "role": "Software Engineer",
            "experience_level": "Mid",
            "technical_skills": ["Python"],
            "soft_skills": [],
            "responsibilities": [],
            "tools": [],
            "difficulty": "medium"
        }

# Streamlit App
st.set_page_config(page_title="AI Job Assessor", layout="wide")
st.title("🤖 AI-Powered Job Assessment Platform")
st.markdown("---")

# Sidebar for JD Input
st.sidebar.header("📄 Job Description")
jd_text = st.sidebar.text_area(
    "Paste Job Description here:",
    height=200,
    placeholder="""We are hiring a Full Stack Developer with 3+ years experience...
Required: React, Node.js, MongoDB, AWS..."""
)

if st.sidebar.button("🔍 Analyze JD", type="primary"):
    if jd_text:
        with st.spinner("Parsing with AI..."):
            jd_data = parse_jd(jd_text)
            st.session_state.jd_data = jd_data
            st.success("✅ JD Parsed Successfully!")
    else:
        st.error("Please enter a Job Description")

# Main Content
if "jd_data" in st.session_state:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📊 Extracted Skills")
        st.json(st.session_state.jd_data)
        
        # Skill weights for later scoring
        tech_weights = {skill: 1.0/len(st.session_state.jd_data["technical_skills"]) 
                       for skill in st.session_state.jd_data["technical_skills"]}
        st.subheader("Skill Weights")
        st.write(tech_weights)
    
    with col2:
        st.header("🎯 Next Steps")
        st.info("Ready to generate assessment questions!")
        if st.button("❓ Generate Questions", type="secondary"):
            st.session_state.questions_ready = True
            st.success("✅ Questions will be generated in Phase 3!")
        st.markdown("---")
        st.caption("Phase 2 Complete ✅")

else:
    st.info("👈 Paste a Job Description in sidebar to begin")
    
    # Sample JD for demo
    st.subheader("💡 Try Sample JD")
    sample_jd = """Senior Python Developer (3-5 years)
Skills: Python, Django, PostgreSQL, Docker, AWS
Responsibilities: Build scalable APIs, lead team, code review"""
    if st.button("Load Sample JD"):
        st.session_state.jd_data = parse_jd(sample_jd)
