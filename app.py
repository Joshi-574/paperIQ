import streamlit as st
import fitz  # PyMuPDF
import os
import tempfile
import re
from collections import Counter

# Set page configuration
st.set_page_config(
    page_title="PaperIQ - Research Paper Analyzer",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'sections' not in st.session_state:
    st.session_state.sections = {}

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        text = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        with fitz.open(tmp_path) as doc:
            for page in doc:
                text += page.get_text()
        
        os.unlink(tmp_path)
        return text
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return ""

def extract_text_from_txt(file):
    """Extract text from TXT file"""
    try:
        return file.read().decode("utf-8")
    except:
        return str(file.read())

def analyze_paper_structure(text):
    """Analyze paper structure and extract sections"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    sections = {
        'title': '',
        'authors': '',
        'abstract': [],
        'introduction': [],
        'methodology': [],
        'results': [],
        'discussion': [],
        'conclusion': [],
        'references': []
    }
    
    current_section = None
    section_patterns = {
        'abstract': r'abstract|summary',
        'introduction': r'introduction|background|motivation',
        'methodology': r'method|methodology|approach|experiment|procedure|materials',
        'results': r'result|finding|outcome|data|experiment',
        'discussion': r'discussion|analysis|interpretation',
        'conclusion': r'conclusion|concluding|summary',
        'references': r'reference|bibliography|citation'
    }
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Detect title (first substantial line)
        if i == 0 and len(line) > 10 and len(line) < 200:
            sections['title'] = line
        
        # Detect authors (lines with academic indicators)
        elif i < 5 and any(indicator in line_lower for indicator in 
                          ['university', 'institute', 'department', 'college', '@', 'email']):
            sections['authors'] = line
        
        # Detect section headers
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line) < 150:
                current_section = section
                break
        
        # Add content to current section
        if current_section and len(line) > 20:
            if len(sections[current_section]) < 50:  # Limit lines per section
                sections[current_section].append(line)
    
    return sections

def generate_comprehensive_summary(text):
    """Generate concise yet comprehensive summary"""
    sections = analyze_paper_structure(text)
    
    summary_parts = []
    
    # Title - always include
    if sections['title']:
        summary_parts.append(f"**📄 Title:** {sections['title']}")
    else:
        # Extract first meaningful line as title
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3]:
            if len(line) > 10 and len(line) < 200:
                summary_parts.append(f"**📄 Title:** {line}")
                break
    
    # Authors
    if sections['authors']:
        summary_parts.append(f"**👥 Authors:** {sections['authors']}")
    
    # Key findings in bullet points
    key_points = []
    
    # Abstract if available
    if sections['abstract']:
        abstract_text = ' '.join(sections['abstract'][:5])
        key_points.append(f"**Abstract:** {abstract_text[:200]}...")
    
    # Main sections as bullet points
    section_bullets = {
        'introduction': 'Research Focus',
        'methodology': 'Method Used', 
        'results': 'Key Findings',
        'conclusion': 'Conclusions'
    }
    
    for section, description in section_bullets.items():
        if sections[section]:
            content = ' '.join(sections[section][:3])
            key_points.append(f"**{description}:** {content[:150]}...")
    
    if key_points:
        summary_parts.append("## 🔍 Key Points")
        for point in key_points:
            summary_parts.append(f"• {point}")
    
    # If very little structure found, provide essential info
    if len(summary_parts) < 3:
        summary_parts.append("## 📖 Document Content")
        # Provide first 400 characters as overview
        overview = text[:400] + "..." if len(text) > 400 else text
        summary_parts.append(overview)
    
    return "\n\n".join(summary_parts)

def answer_question_offline(question, text):
    """Answer questions with concise one-line answers when possible"""
    question_lower = question.lower().strip()
    sections = analyze_paper_structure(text)
    
    # Common simple questions with direct answers
    simple_questions = {
        'what is artificial intelligence': "AI refers to machines that can perform tasks typically requiring human intelligence.",
        'what is ai': "AI refers to machines that can perform tasks typically requiring human intelligence.",
        'what is machine learning': "Machine learning is a subset of AI that enables computers to learn without explicit programming.",
        'what is deep learning': "Deep learning uses neural networks with multiple layers to analyze various data types.",
        'what is neural network': "Neural networks are computing systems inspired by the human brain that recognize patterns.",
        'what is data science': "Data science combines statistics, programming, and domain knowledge to extract insights from data.",
        'what is computer vision': "Computer vision enables computers to interpret and understand visual information from the world.",
        'what is natural language processing': "NLP enables computers to understand, interpret, and generate human language.",
        'what is robotics': "Robotics involves designing and operating machines that can perform tasks automatically.",
        'who are the authors': f"Authors: {sections['authors'] if sections['authors'] else 'Not specified in the paper'}",
        'what is the title': f"Title: {sections['title'] if sections['title'] else 'Not clearly specified'}",
        'what is the abstract': "The abstract summarizes the paper's main objectives, methods, results, and conclusions.",
    }
    
    # Check if it's a simple question with predefined answer
    for simple_q, answer in simple_questions.items():
        if simple_q in question_lower:
            return f"**🤖 {answer}**"
    
    # Paper-specific questions with concise answers
    if any(word in question_lower for word in ['title', 'what is the paper about', 'name of paper']):
        return f"**📄 {sections['title'] if sections['title'] else 'Title not explicitly stated'}**"
    
    elif any(word in question_lower for word in ['author', 'who wrote', 'who is the author']):
        return f"**👥 {sections['authors'] if sections['authors'] else 'Authors not specified'}**"
    
    elif any(word in question_lower for word in ['abstract', 'summary', 'overview']):
        if sections['abstract']:
            abstract_preview = ' '.join(sections['abstract'][:3])[:100] + "..."
            return f"**📝 {abstract_preview}**"
        return "**📝 Abstract section not found in this paper**"
    
    elif any(word in question_lower for word in ['method', 'methodology', 'approach', 'how did they']):
        if sections['methodology']:
            return "**🔬 Research methodology details are in the methods section**"
        return "**🔬 Methodology section not explicitly identified**"
    
    elif any(word in question_lower for word in ['result', 'finding', 'outcome', 'what did they find']):
        if sections['results']:
            return "**📊 Key findings and results are detailed in the results section**"
        return "**📊 Results section not explicitly identified**"
    
    elif any(word in question_lower for word in ['conclusion', 'conclude', 'what was concluded']):
        if sections['conclusion']:
            return "**💡 Conclusions summarize the research outcomes and implications**"
        return "**💡 Conclusion section not explicitly identified**"
    
    elif any(word in question_lower for word in ['purpose', 'goal', 'objective', 'why', 'aim']):
        if sections['introduction']:
            return "**🎯 Research objectives are outlined in the introduction section**"
        return "**🎯 Research purpose described in the introduction**"
    
    elif any(word in question_lower for word in ['what is', 'what are', 'define']):
        # Extract the term being defined
        words = question_lower.split()
        if 'what is' in question_lower or 'what are' in question_lower:
            term_start = question_lower.find('what is') + 8 if 'what is' in question_lower else question_lower.find('what are') + 9
            term = question_lower[term_start:].strip('? ')
            
            if term:
                # Search for definition in text
                lines = text.split('\n')
                for line in lines:
                    line_lower = line.lower()
                    if term in line_lower and len(line) > 20 and len(line) < 300:
                        # Clean up the line for response
                        clean_line = line.strip()
                        if len(clean_line) > 150:
                            clean_line = clean_line[:150] + "..."
                        return f"**📚 {clean_line}**"
                
                return f"**❓ Information about '{term}' not found in this paper**"
    
    # For very general questions, provide helpful guidance
    if len(question.split()) <= 4:  # Very short questions
        return "**🤖 Please ask specific questions about this research paper's content, methods, or findings**"
    
    # Keyword-based concise answer for other questions
    keywords = [word for word in question_lower.split() if len(word) > 3]
    relevant_lines = []
    
    for line in text.split('\n'):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords) and 30 < len(line.strip()) < 200:
            relevant_lines.append(line.strip())
    
    if relevant_lines:
        # Take the most relevant line
        best_line = relevant_lines[0]
        if len(best_line) > 120:
            best_line = best_line[:120] + "..."
        return f"**🔍 {best_line}**"
    
    # Final fallback - concise response
    return "**❓ Specific answer not found in this paper. Try asking about the title, authors, methods, or results.**"

def main():
    st.title("📚 PaperIQ - Research Paper Analyzer")
    st.markdown("**🆓 Offline Version - No Internet Required**")
    st.markdown("---")
    
    # Navigation
    st.sidebar.title("🧭 Navigation")
    option = st.sidebar.radio(
        "Choose an option:",
        ["Upload & Analyze", "Paper Summary", "Chat with Paper", "About"]
    )
    
    if option == "Upload & Analyze":
        st.header("📄 Upload Research Paper")
        
        uploaded_file = st.file_uploader(
            "Upload your research paper (PDF or TXT files)",
            type=['pdf', 'txt'],
            help="Works completely offline - no API keys needed"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 **File:** {uploaded_file.name} | **Type:** {uploaded_file.type}")
            
            with st.spinner("🔍 Extracting and analyzing document..."):
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_txt(uploaded_file)
            
            if text and len(text.strip()) > 100:
                st.session_state.processed_text = text
                st.session_state.sections = analyze_paper_structure(text)
                
                st.success("✅ Document processed successfully!")
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Characters", f"{len(text):,}")
                with col2:
                    st.metric("Words", f"{len(text.split()):,}")
                with col3:
                    sections_found = sum(1 for section in st.session_state.sections.values() if section)
                    st.metric("Sections Found", sections_found)
                with col4:
                    st.metric("Status", "Ready ✅")
                
                # Show detected sections
                with st.expander("🔍 Detected Paper Structure"):
                    for section, content in st.session_state.sections.items():
                        if content:
                            st.write(f"**{section.upper()}:** {len(content)} lines detected")
                
                # Text preview
                with st.expander("📖 View Text Preview"):
                    preview_text = text[:1500] + "..." if len(text) > 1500 else text
                    st.text_area("Extracted Content", preview_text, height=300, label_visibility="collapsed")
            
            else:
                st.error("❌ Could not extract sufficient text. Please try another file.")
    
    elif option == "Paper Summary":
        st.header("📝 Paper Summary")
        
        if not st.session_state.processed_text:
            st.warning("⚠️ Please upload a research paper in the 'Upload & Analyze' section first.")
        else:
            # Generate summary
            if not st.session_state.summary:
                with st.spinner("🤖 Analyzing paper content and structure..."):
                    st.session_state.summary = generate_comprehensive_summary(st.session_state.processed_text)
            
            st.markdown(st.session_state.summary)
            
            # Regenerate button
            if st.button("🔄 Regenerate Summary", type="secondary"):
                with st.spinner("🤖 Creating new summary..."):
                    st.session_state.summary = generate_comprehensive_summary(st.session_state.processed_text)
                st.rerun()
    
    elif option == "Chat with Paper":
        st.header("💬 Chat with Paper")
        
        if not st.session_state.processed_text:
            st.warning("⚠️ Please upload a research paper first.")
        else:
            st.info("""
            💡 **Ask questions about:**
            • Title & Authors
            • Abstract & Overview  
            • Methodology & Approach
            • Results & Findings
            • Conclusions & Discussion
            • Research Purpose & Goals
            """)
            
            question = st.text_input(
                "Your question:",
                placeholder="e.g., What is the main research question? What methodology was used?",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns([4, 1])
            with col2:
                ask_btn = st.button("🚀 Ask Question", use_container_width=True)
            
            if ask_btn and question:
                with st.spinner("🔍 Searching paper content..."):
                    answer = answer_question_offline(question, st.session_state.processed_text)
                    st.session_state.chat_history.append((question, answer))
                
                st.subheader("📋 Answer:")
                st.markdown(answer)
            
            # Display chat history
            if st.session_state.chat_history:
                st.subheader("💭 Conversation History")
                for i, (q, a) in enumerate(reversed(st.session_state.chat_history[-5:])):
                    st.write(f"**🙋 Question {i+1}:** {q}")
                    st.write(f"**🤖 Answer:** {a}")
                    st.markdown("---")
            
            # Clear history
            if st.session_state.chat_history and st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
    
    elif option == "About":
        st.header("ℹ️ About PaperIQ")
        st.markdown("""
        ### Offline Research Paper Analyzer
        
        **✨ Features:**
        - 📄 Upload PDF/TXT research papers
        - 📝 Intelligent offline summarization
        - 💬 Smart Q&A without internet
        - 🔍 Automatic section detection
        - 🆓 Completely free & offline
        
        **🚀 Benefits:**
        - No API keys required
        - No internet connection needed
        - No rate limits
        - Complete privacy
        - Instant processing
        
        **🔧 How It Works:**
        - Uses advanced text analysis algorithms
        - Detects paper structure automatically
        - Extracts key information intelligently
        - Provides contextual answers
        
        **⚡ Installation:**
        ```bash
        pip install streamlit pymupdf
        streamlit run app.py
        ```
        
        **📞 Note:** This version works completely offline. No external services are used.
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "PaperIQ - Offline Research Paper Analyzer | No Internet Required"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()