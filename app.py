import streamlit as st
import document_processor as dp
import ai_engine as ai
import os

st.set_page_config(page_title="AI Document Assistant", page_icon="🧠", layout="wide")

# Custom UI Styles
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    div[data-testid="stSidebar"] {
        background-color: #1E1E2E;
    }
    h1, h2, h3 {
        color: #61AFEF;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #61AFEF;
        color: #282C34;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #61AFEF;
        opacity: 0.8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🧠 AI-Powered Document Assistant & Quiz Gen")
    st.markdown("An enterprise-grade NLP agent engineered to digest complex documents, synthesize context, and autonomously generate intelligent assessments.")
    
    with st.sidebar:
        st.title("⚙️ Configuration")
        api_key = st.text_input("Google Gemini API Key", type="password")
        if not api_key:
            st.warning("Please enter your API key to proceed.")
            
        st.subheader("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload your PDFs, Word Docs, or Text files here and click 'Process'",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt']
        )
        
        if st.button("Process Documents"):
            if not api_key:
                st.error("API Key is required!")
            elif not uploaded_files:
                st.error("Please upload multiple documents!")
            else:
                with st.spinner("Processing & embedding document chunks..."):
                    raw_text = dp.process_documents(uploaded_files)
                    if raw_text.strip():
                        text_chunks = ai.get_text_chunks(raw_text)
                        try:
                            ai.get_vector_store(text_chunks, api_key)
                            st.success("Processing Complete! Vector Database Ready ✅")
                        except Exception as e:
                            st.error(f"Failed to communicate with Google Gemini API: {str(e)}")
                            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                st.warning("⚠️ **Your API Key has exceeded its quota limits.** Please generate a new key on Google AI Studio or check your billing plan.")
                    else:
                        st.error("Could not extract any meaningful text from the documents.")

    tab1, tab2 = st.tabs(["💬 Document Q&A", "📝 Quiz Generator"])

    with tab1:
        st.header("Ask Questions about your Documents")
        user_question = st.text_input("Ask a question based on the uploaded material:")
        
        if st.button("Get Answer") and user_question:
            if not api_key:
                st.warning("Please provide your Gemini API Key in the sidebar.")
            elif not os.path.exists("faiss_index_dir"):
                st.warning("Please upload and process a document first to build the knowledge base.")
            else:
                with st.spinner("Searching for answers..."):
                    try:
                        response = ai.user_input(user_question, api_key)
                        st.markdown("### Answer")
                        st.info(response)
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            st.warning("⚠️ **Your API Key has exceeded its quota limits.** Please generate a new key on Google AI Studio or check your billing plan.")
                        else:
                            st.error(f"Generation failed: {str(e)}")

    with tab2:
        st.header("Generate Assessment")
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
        with col2:
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard", "Expert"])
            
        if st.button("Generate Quiz ✨"):
            if not api_key:
                st.warning("Please provide your Gemini API Key in the sidebar.")
            elif not os.path.exists("faiss_index_dir"):
                st.warning("Please upload and process a document first to build the knowledge base.")
            else:
                with st.spinner("Synthesizing context and generating questions..."):
                    try:
                        quiz_data = ai.generate_quiz(api_key, num_questions, difficulty)
                        
                        if isinstance(quiz_data, dict) and "error" in quiz_data:
                            st.error(f"Failed to generate quiz: {quiz_data['error']}")
                        elif not isinstance(quiz_data, list):
                            st.error("Received an invalid format from the server. Please try again.")
                        else:
                            st.session_state['quiz'] = quiz_data
                            st.session_state['quiz_submitted'] = False
                            st.session_state['user_answers'] = {}
                            st.success("Quiz Generated!")
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            st.warning("⚠️ **Your API Key has exceeded its quota limits.** Please generate a new key on Google AI Studio or check your billing plan.")
                        else:
                            st.error(f"Quiz Generation failed: {str(e)}")
                        
        if 'quiz' in st.session_state:
            st.markdown("---")
            st.subheader("Quiz")
            
            # Using forms could be better to avoid instant re-renders, but standard layout works too.
            with st.form(key='quiz_form'):
                # Build inputs dynamically
                for i, q in enumerate(st.session_state['quiz']):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    # We store answers in session state explicitly outside the form processing if needed, 
                    # but Streamlit forms handle state collection well.
                    st.radio(f"Select answer for Q{i+1}", q['options'], key=f"ans_{i}")
                    st.markdown("") # Spacing
                    
                submit_button = st.form_submit_button(label='Submit Answers')
                
            if submit_button:
                st.session_state['quiz_submitted'] = True
                
            if st.session_state.get('quiz_submitted', False):
                score = 0
                st.markdown("### Results")
                for i, q in enumerate(st.session_state['quiz']):
                    user_ans = st.session_state[f"ans_{i}"]
                    correct_ans = q['answer']
                    
                    if user_ans == correct_ans:
                        score += 1
                        st.success(f"**Q{i+1}: Correct!** ✅  \nYour Answer: {user_ans}  \n_Explanation:_ {q.get('explanation', '')}")
                    else:
                        st.error(f"**Q{i+1}: Incorrect.** ❌  \nYour Answer: {user_ans}  \n**Correct Answer:** {correct_ans}  \n_Explanation:_ {q.get('explanation', '')}")
                        
                st.markdown(f"## Final Score: {score}/{len(st.session_state['quiz'])}")

if __name__ == "__main__":
    main()
