#!/usr/bin/env python3
"""
Financial RAG Chatbot - Streamlit UI

A simple chat interface for the Financial RAG Chatbot system.
Features:
- Modern chat interface with message bubbles
- File upload for PDFs
- Chat history and conversation management
- Real-time responses from the FastAPI backend
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
import base64
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Financial RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for WhatsApp-like interface
st.markdown("""
<style>
    /* Main container styling */
    .main-container {
        background-color: #f0f2f6;
        padding: 0;
        margin: 0;
    }
    
    /* Remove top padding */
    .st-emotion-cache-z5fcl4 {
        padding-top: 1rem !important;
    }
    
    /* Chat header styling */
    .chat-header {
        background-color: #f8f9fa;
        padding: 15px 20px;
        border-bottom: 1px solid #e9ecef;
        border-radius: 10px 10px 0 0;
        margin: 10px 10px 0 10px;
    }
    
    /* Chat messages container (scrollable) */
    .chat-container {
        height: 60vh;
        padding: 20px;
        overflow-y: auto;
        background-color: #ffffff;
        border-left: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        margin: 0 10px;
        scroll-behavior: smooth;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-radius: 0;
    }
    
    /* Custom scrollbar for chat container */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Chat input area styling */
    .chat-input-area {
        background-color: #f8f9fa;
        padding: 15px 20px;
        border-top: 1px solid #e9ecef;
        border-radius: 0 0 10px 10px;
        margin: 0 10px 10px 10px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        margin-bottom: 1rem;
    }
    
    /* User messages on the right */
    .stChatMessage[data-testid="user-message"] {
        margin-left: 20%;
        display: flex;
        justify-content: flex-end;
    }
    
    .stChatMessage[data-testid="user-message"] .stChatMessage__content {
        background-color: #007bff !important;
        color: white !important;
        border-radius: 18px 18px 5px 18px !important;
        padding: 12px 16px !important;
        margin-left: auto !important;
        max-width: 80% !important;
        text-align: left !important;
    }
    
    /* Assistant messages on the left */
    .stChatMessage[data-testid="assistant-message"] {
        margin-right: 20%;
        display: flex;
        justify-content: flex-start;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stChatMessage__content {
        background-color: #f1f3f4 !important;
        color: #333 !important;
        border-radius: 18px 18px 18px 5px !important;
        padding: 12px 16px !important;
        margin-right: auto !important;
        max-width: 80% !important;
        text-align: left !important;
    }
    
    /* Alternative selectors for better compatibility */
    div[data-testid="user-message"] {
        margin-left: 20% !important;
        display: flex !important;
        justify-content: flex-end !important;
    }
    
    div[data-testid="assistant-message"] {
        margin-right: 20% !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    
    /* Button styling */
    .stButton > button {
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* Chat input styling */
    .stChatInput {
        margin-top: 1rem;
    }
    
    /* Quick actions styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Section dividers */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Message bubbles */
    .user-message {
        background-color: #dcf8c6;
        padding: 10px 15px;
        border-radius: 18px 18px 5px 18px;
        margin: 5px 0;
        margin-left: 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    .bot-message {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 5px;
        margin: 5px 0;
        margin-right: 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #e5e5e5;
        word-wrap: break-word;
    }
    
    /* Agent indicator */
    .agent-indicator {
        font-size: 0.8em;
        color: #666;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    /* Timestamp */
    .message-time {
        font-size: 0.7em;
        color: #999;
        text-align: right;
        margin-top: 5px;
    }
    
    
    
    /* File upload area */
    .upload-area {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 10px 0;
    }
    
    /* Agent selection buttons */
    .agent-button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .agent-button:hover {
        background-color: #0056b3;
    }
    
    .agent-button.selected {
        background-color: #28a745;
    }
    
    /* Status indicators */
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* MCQ Question Styling */
    .mcq-question {
        background-color: #f8f9fa;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .mcq-options {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    .mcq-option {
        margin: 8px 0;
        padding: 8px 12px;
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        font-size: 0.95em;
    }
    
    .mcq-answers {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin-top: 20px;
        font-size: 0.9em;
    }
    
    .mcq-answer-item {
        margin: 8px 0;
        padding: 5px 0;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>

<script>
// Auto-scroll to bottom of chat container
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Plus button functionality
function initPlusButton() {
    const plusButton = document.querySelector('.plus-button');
    const plusMenu = document.querySelector('.plus-menu');
    
    if (plusButton && plusMenu) {
        plusButton.addEventListener('click', function(e) {
            e.stopPropagation();
            plusMenu.classList.toggle('show');
            plusButton.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!plusButton.contains(e.target) && !plusMenu.contains(e.target)) {
                plusMenu.classList.remove('show');
                plusButton.classList.remove('active');
            }
        });
        
        // Handle menu item clicks
        const menuItems = plusMenu.querySelectorAll('.plus-menu-item');
        menuItems.forEach(function(item) {
            item.addEventListener('click', function() {
                const action = this.dataset.action;
                handleMenuAction(action);
                plusMenu.classList.remove('show');
                plusButton.classList.remove('active');
            });
        });
    }
}

// Handle menu actions
function handleMenuAction(action) {
    switch(action) {
        case 'upload':
            // Trigger file upload
            const fileInput = document.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.click();
            }
            break;
        case 'summarize':
            // Auto-fill summarize request
            const textInput = document.querySelector('.text-input');
            if (textInput) {
                textInput.value = 'Please summarize this document';
                textInput.focus();
            }
            break;
        case 'mcq':
            // Auto-fill MCQ request
            const textInput2 = document.querySelector('.text-input');
            if (textInput2) {
                textInput2.value = 'Generate 5 MCQ questions from this document';
                textInput2.focus();
            }
            break;
        case 'analyze':
            // Auto-fill analysis request
            const textInput3 = document.querySelector('.text-input');
            if (textInput3) {
                textInput3.value = 'Analyze the key trends and insights in this data';
                textInput3.focus();
            }
            break;
        case 'clear':
            // Clear chat history
            if (confirm('Are you sure you want to clear the chat history?')) {
                // This would need to be handled by Streamlit
                console.log('Clear chat requested');
            }
            break;
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    scrollToBottom();
    initPlusButton();
});

// Scroll to bottom when new content is added
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            setTimeout(scrollToBottom, 100);
        }
    });
});

// Start observing when the chat container is available
const checkForChatContainer = setInterval(function() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
        clearInterval(checkForChatContainer);
    }
}, 100);
</script>
""", unsafe_allow_html=True)

class FinancialRAGChatbotUI:
    """Main UI class for the Financial RAG Chatbot."""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
    
    
    def send_message(self, message: str, document_id: Optional[str] = None) -> Dict:
        """Send a message to the API and get response."""
        try:
            payload = {
                "message": message,
                "document_id": document_id
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat", 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}
    
    def upload_multiple_files(self, files: List[bytes], filenames: List[str]) -> List[Dict]:
        """Upload multiple files to the API."""
        try:
            # Prepare files for upload - FastAPI expects multiple files with same field name
            file_data = []
            for file_content, filename in zip(files, filenames):
                file_data.append(("files", (filename, file_content, "application/octet-stream")))
            
            response = requests.post(f"{self.api_base_url}/upload/multiple", files=file_data, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                return [{"error": f"Upload failed: {response.text}"}]
                
        except Exception as e:
            return [{"error": f"Upload error: {str(e)}"}]
    
    def get_documents(self) -> List[Dict]:
        """Get list of uploaded documents."""
        try:
            response = requests.get(f"{self.api_base_url}/documents")
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def render_chat_message(self, message: str, is_user: bool, timestamp: str = None, sources: List = None):
        """Render a single chat message with enhanced styling."""
        if is_user:
            st.markdown(f"""
            <div class="user-message">
                {message}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Add sources if available
            sources_info = ""
            if sources and len(sources) > 0:
                sources_info = f'<div style="font-size: 0.8em; color: #666; margin-top: 5px;">📎 Sources: {len(sources)}</div>'
            
            st.markdown(f"""
            <div class="bot-message">
                <div class="agent-indicator">🤖 RAG Chatbot</div>
                {message}
                {sources_info}
                <div class="message-time">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def upload_files(self, uploaded_files):
        """Upload files to the API."""
        try:
            # Prepare files for multipart/form-data upload
            files = []
            for uploaded_file in uploaded_files:
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                # Read file content once
                file_content = uploaded_file.read()
                files.append(('files', (uploaded_file.name, file_content, uploaded_file.type)))
            
            response = requests.post(
                f"{self.api_base_url}/upload/multiple",
                files=files,
                timeout=120  # Increased timeout for large files
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Upload failed with status {response.status_code}: {response.text}"}
        except requests.exceptions.Timeout:
            return {"error": "Upload timeout - file may be too large"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed - please check if API server is running"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Upload request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def handle_file_upload(self, uploaded_files):
        """Handle file upload and process them."""
        if not uploaded_files:
            return
        
        if len(uploaded_files) > 10:
            st.error("❌ Maximum 10 files allowed per upload")
            return
        
        
        # Show loading message
        loading_placeholder = st.empty()
        loading_placeholder.info(f"🔄 Uploading {len(uploaded_files)} files...")
        
        try:
            # Upload files via API
            upload_response = self.upload_files(uploaded_files)
            
            if upload_response and isinstance(upload_response, list) and len(upload_response) > 0:
                # Check if any files were successfully processed
                successful_uploads = [r for r in upload_response if r.get("status") == "processed"]
                
                if successful_uploads:
                    # Clear loading message
                    loading_placeholder.empty()
                    st.success(f"✅ Successfully uploaded {len(successful_uploads)} files!")
                    
                    # Update session state
                    for response_item in successful_uploads:
                        document_id = response_item.get("document_id")
                        filename = response_item.get("filename")
                        document_type = response_item.get("document_type")
                        
                        if document_type == "pdf":
                            st.session_state.uploaded_pdf_documents.append({
                                "id": document_id,
                                "filename": filename,
                                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                    
                    st.rerun()
                else:
                    loading_placeholder.empty()
                    st.error("❌ No files were successfully processed")
            elif upload_response and "error" in upload_response:
                loading_placeholder.empty()
                st.error(f"❌ Upload failed: {upload_response['error']}")
            else:
                loading_placeholder.empty()
                st.error("❌ Upload failed: No response received")
                
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ Upload failed: {str(e)}")
    
    def render_chat_interface(self):
        """Render the chat interface using Streamlit's native components."""
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Document selection is now handled in Row 2 above
        
        # Chat header with Clear Chat button on extreme right
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            st.markdown("### Chat")
        
        with col2:
            st.write("")  # Empty space
        
        with col3:
            # Clear chat button positioned at extreme right
            if st.button("🗑️ Clear Chat", help="Clear all chat messages"):
                st.session_state.messages = []
                st.rerun()
        
        # Create a container for messages with fixed height
        messages_container = st.container()
        
        with messages_container:
            # Display chat messages using Streamlit's native components
            for message in st.session_state.messages:
                if message["is_user"]:
                    with st.chat_message("user"):
                        st.write(message["content"])
                        st.caption(f"Sent at {message.get('timestamp', '')}")
                else:
                    with st.chat_message("assistant"):
                        # Show message content
                        st.write(message["content"])
                        
                        # Show sources if available
                        if message.get("sources") and len(message["sources"]) > 0:
                            with st.expander(f"📎 Sources ({len(message['sources'])})"):
                                for i, source in enumerate(message["sources"]):
                                    st.write(f"**Source {i+1}:**")
                                    st.write(source.get("content", "")[:200] + "...")
                                    if source.get("metadata"):
                                        st.write(f"*From: {source['metadata'].get('filename', 'Unknown')}*")
                        
                        st.caption(f"Responded at {message.get('timestamp', '')}")
        
        
        # Message input
        st.markdown("---")
        st.markdown("### 💬 Send Message")
        user_input = st.chat_input(
            "Ask me anything about your financial documents...",
            key="chat_input"
        )
        
        # Process message
        if user_input:
            # Add user message to chat
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "content": user_input,
                "is_user": True,
                "timestamp": timestamp
            })
            
            # Check if documents are available
            pdf_docs = st.session_state.get('uploaded_pdf_documents', [])
            total_docs = len(pdf_docs)
            
            if total_docs == 0:
                st.error("❌ Please upload documents first!")
                st.stop()
            
            # Send to API and get response
            loading_message = "🤖 Processing your question..."
            
            with st.spinner(loading_message):
                response = self.send_message(user_input, None)
            
            # Add bot response to chat
            if "error" not in response:
                bot_message = response.get("response", "No response received")
                sources = response.get("sources", [])
                
                st.session_state.messages.append({
                    "content": bot_message,
                    "is_user": False,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "sources": sources
                })
            else:
                st.session_state.messages.append({
                    "content": f"❌ Error: {response['error']}",
                    "is_user": False,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "sources": []
                })
            
            st.rerun()
    
    def render_welcome_screen(self):
        """Render welcome screen."""
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1>🤖 Financial RAG Chatbot</h1>
            <h3>Welcome to your AI-powered financial assistant!</h3>
            <p style="font-size: 18px; color: #666;">
                Upload your financial PDF documents and start asking questions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📄 Document Analysis
            - Upload PDF financial reports
            - Ask questions about your documents
            - Get intelligent answers based on document content
            - View source citations
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 RAG Technology
            - Retrieval-Augmented Generation
            - Context-aware responses
            - Document similarity search
            - Accurate financial insights
            """)
    
    def run(self):
        """Main application runner."""
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'uploaded_pdf_documents' not in st.session_state:
            st.session_state.uploaded_pdf_documents = []
        if 'pdf_document_id' not in st.session_state:
            st.session_state.pdf_document_id = None
        if 'selected_agent' not in st.session_state:
            st.session_state.selected_agent = "Q&A"
        
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, #007bff, #28a745); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🤖 Financial RAG Chatbot</h1>
            <p>AI-powered financial document analysis and Q&A</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Row 1: Browse Documents and Selected Files
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # File upload
            uploaded_files = st.file_uploader(
                "Browse Documents",
                type=['pdf'],
                accept_multiple_files=True,
                help="Select PDF files to upload"
            )
        
        with col2:
            # Show selected files
            if uploaded_files:
                st.write(f"📁 Selected {len(uploaded_files)} file(s):")
                for file in uploaded_files:
                    st.write(f"• {file.name}")
                
                # Upload button
                if st.button("📤 Upload Files", type="primary"):
                    self.handle_file_upload(uploaded_files)
            else:
                st.write("📁 No files selected")
        
        # Main content area
        self.render_chat_interface()

def main():
    """Main function to run the Streamlit app."""
    app = FinancialRAGChatbotUI()
    app.run()

if __name__ == "__main__":
    main()
