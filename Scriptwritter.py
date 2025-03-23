import os
import json
import streamlit as st
import google.generativeai as genai
import pyperclip
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from firebase_admin.exceptions import FirebaseError
import uuid
from datetime import datetime
import tempfile
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase (Only once)
@st.cache_resource
def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Use the provided Firebase configuration
        cred_dict = {
            "type": "service_account",
            "project_id": "ai-scriptwritter",
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        }

        # Initialize Firebase
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'ai-scriptwritter.appspot.com'
        })
    
    return firestore.client(), storage.bucket()

# Streamlit session state initialization
def initialize_session_state():
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'script' not in st.session_state:
        st.session_state['script'] = ""
    if 'saved_scripts' not in st.session_state:
        st.session_state['saved_scripts'] = []
    if 'show_advanced_options' not in st.session_state:
        st.session_state['show_advanced_options'] = True

def is_valid_email(email):
    """Check if the email is valid using a regex pattern."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


# User Authentication Functions
def register_user(email, password):
    try:
        # Validate email format
        if not is_valid_email(email):
            return False, "Invalid email format. Please enter a valid email address."
        
        # Ensure Firebase is initialized
        db, bucket = initialize_firebase()
        
        # Create user
        user = auth.create_user(
            email=email,
            password=password
        )
        return True, user.uid
    except FirebaseError as e:
        return False, str(e)

def login_user(email, password):
    try:
        # Ensure Firebase is initialized
        db, bucket = initialize_firebase()
        
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # In a real implementation, you would verify the password against Firebase Auth
        # Here we're simulating successful authentication
        return True, user.uid
    except FirebaseError as e:
        return False, str(e)
    


# Cloud Storage Functions
def save_script_to_cloud(user_id, script_name, script_text):
    db, bucket = initialize_firebase()
    
    # Create a unique ID for the script
    script_id = str(uuid.uuid4())
    
    # Create script metadata
    script_data = {
        "id": script_id,
        "name": script_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "user_id": user_id
    }
    
    # Save metadata to Firestore
    db.collection('users').document(user_id).collection('scripts').document(script_id).set(script_data)
    
    # Save actual script content to Cloud Storage
    blob = bucket.blob(f"scripts/{user_id}/{script_id}.txt")
    blob.upload_from_string(script_text)
    
    return True, script_id

def load_scripts_from_cloud(user_id):
    if not user_id:
        return []
        
    db, bucket = initialize_firebase()
    
    # Get all script metadata for this user
    scripts_ref = db.collection('users').document(user_id).collection('scripts')
    scripts = scripts_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).get()
    
    script_list = []
    for script in scripts:
        script_data = script.to_dict()
        
        # Get content from Cloud Storage
        blob = bucket.blob(f"scripts/{user_id}/{script_data['id']}.txt")
        try:
            script_content = blob.download_as_text()
            script_data['script'] = script_content
            script_list.append(script_data)
        except Exception:
            # Handle case where content might be missing
            script_data['script'] = "Content not available"
            script_list.append(script_data)
    
    return script_list

def delete_script_from_cloud(user_id, script_id):
    db, bucket = initialize_firebase()
    
    # Delete from Firestore
    db.collection('users').document(user_id).collection('scripts').document(script_id).delete()
    
    # Delete from Cloud Storage
    blob = bucket.blob(f"scripts/{user_id}/{script_id}.txt")
    blob.delete()
    
    return True

# Local Storage Functions (Fallback when offline or not logged in)
def load_saved_scripts():
    if os.path.exists("saved_scripts.json"):
        with open("saved_scripts.json", "r") as file:
            return [json.loads(line) for line in file]
    return []

def save_script(script_name, script_text):
    if script_name.strip() and script_text.strip():
        # If user is logged in, save to cloud
        if st.session_state['user_id']:
            success, script_id = save_script_to_cloud(
                st.session_state['user_id'], 
                script_name, 
                script_text
            )
            if success:
                st.session_state['saved_scripts'] = load_scripts_from_cloud(st.session_state['user_id'])
                st.success("Script saved to your cloud account!")
                return True
        
        # Fallback to local storage
        script_data = {"name": script_name, "script": script_text}
        with open("saved_scripts.json", "a") as file:
            json.dump(script_data, file)
            file.write("\n")
        st.session_state['saved_scripts'].append(script_data)
        st.success("Script saved locally!")
        return True
    else:
        st.error("Please enter a valid name and script before saving.")
        return False

def delete_script(index, script_id=None):
    # If user is logged in and script_id is provided
    if st.session_state['user_id'] and script_id:
        success = delete_script_from_cloud(st.session_state['user_id'], script_id)
        if success:
            st.session_state['saved_scripts'] = load_scripts_from_cloud(st.session_state['user_id'])
            return True
    
    # Fallback to local storage
    saved_scripts = load_saved_scripts()
    if 0 <= index < len(saved_scripts):
        del saved_scripts[index]
        with open("saved_scripts.json", "w") as file:
            for script in saved_scripts:
                json.dump(script, file)
                file.write("\n")
        st.session_state['saved_scripts'] = saved_scripts
        return True
    
    return False

# Load prompt templates
def load_prompt_templates():
    templates = {
        "Tutorial": {
            "structure": "Introduction with problem statement, Step-by-step instructions, Tips and tricks, Summary and call to action",
            "example": "Today I'll show you how to solve [problem]. First, let's understand why this matters..."
        },
        "Product Review": {
            "structure": "Introduction to product, Key features overview, Pros and cons, Personal experience, Final verdict",
            "example": "I've been using [product] for [timeframe], and today I'm sharing my honest thoughts..."
        },
        "Storytelling": {
            "structure": "Hook/attention grabber, Background/context, Main narrative, Lesson/takeaway, Call to action",
            "example": "Have you ever wondered what would happen if [scenario]? Well, last week I found out when..."
        },
        "Educational": {
            "structure": "Intriguing question or fact, Why this topic matters, Main teaching points, Practical applications, Summary",
            "example": "Did you know that [interesting fact]? In this video, we'll explore the science behind..."
        },
        "Vlog": {
            "structure": "Day/event introduction, Main activities/highlights, Reflections/thoughts, Preview of next content",
            "example": "Welcome back to my channel! Today I'm taking you with me to [place/event]..."
        }
    }
    return templates

# Generate enhanced prompt
def generate_enhanced_prompt(main_points, tone_style, target_audience, video_length, language, 
                             seo_keywords, use_case, template_choice, include_sections, 
                             advanced_options=None):
    
    # Load template structure
    templates = load_prompt_templates()
    selected_template = templates.get(template_choice, {"structure": "", "example": ""})
    
    # Parse video length into actual minutes
    length_map = {
        "Short (1-3 min)": "1-3 minutes",
        "Medium (3-5 min)": "3-5 minutes",
        "Long (5-10 min)": "5-10 minutes"
    }
    duration = length_map.get(video_length, video_length)
    
    # Calculate approximate word count based on video length
    min_length = int(duration.split("-")[0]) * 150 if "-" in duration else 150
    max_length = int(duration.split("-")[1].split()[0]) * 150 if "-" in duration else 450
    
    # Build sections to include
    sections = []
    if "Introduction" in include_sections:
        sections.append("Introduction")
    if "Main Content" in include_sections:
        sections.append("Main Content")
    if "Call to Action" in include_sections:
        sections.append("Call to Action")
    if "FAQ Section" in include_sections:
        sections.append("FAQ Section")
    if "Resources/Links" in include_sections:
        sections.append("Resources/Links")
    
    # Combined prompt with system instructions and user request
    prompt = f"""
    You are an expert YouTube script writer specializing in {use_case} videos.
    Your task is to create a compelling, engaging script in {language} that feels natural when spoken.
    Target a {duration} video (approximately {min_length}-{max_length} words).
    
    AUDIENCE:
    The target audience is {', '.join(target_audience)}.
    
    TONE AND STYLE:
    Write in a {tone_style.lower()} tone that resonates with the audience.
    
    FORMAT:
    - Create a two-column script format with [VISUAL] and [NARRATION] sections
    - Include timestamps approximately every 30 seconds
    - Use natural, conversational language (contractions, varied sentence length)
    - Incorporate pauses, emphasis, and transitions where appropriate
    
    STRUCTURE:
    Follow this {template_choice} video structure: {selected_template['structure']}
    
    SEO OPTIMIZATION:
    Naturally incorporate these keywords: {seo_keywords}
    
    SECTIONS TO INCLUDE:
    {', '.join(sections)}
    """
    
    if advanced_options:
        if advanced_options.get("hook_style"):
            prompt += f"\nHOOK STYLE: Create a {advanced_options['hook_style']} hook that immediately captures viewer attention."
        
        if advanced_options.get("storytelling_elements"):
            prompt += f"\nSTORYTELLING ELEMENTS: Incorporate {advanced_options['storytelling_elements']} to make the content more engaging."
        
        if advanced_options.get("transitions"):
            prompt += f"\nTRANSITIONS: Use {advanced_options['transitions']} transitions between sections."
            
        if advanced_options.get("video_editing_cues"):
            prompt += f"\nVIDEO EDITING CUES: Include suggestions for {advanced_options['video_editing_cues']} where appropriate."
    
    prompt += f"""
    
    Now, create a complete YouTube script about: {main_points}
    
    Reference this example style (but do not copy the content): {selected_template['example']}
    """
    
    return prompt

def generate_script_with_advanced_prompts(enhanced_prompt, model_name="gemini-1.5-flash-latest", 
                                          temperature=0.7, top_k=20, top_p=0.9):
    """Generates a YouTube script using advanced prompt engineering."""
    try:
        # Configure API key - in production use environment variables
        API_KEY = "AIzaSyB8CLIP4vwf6QEYZJ5LsBrX3ZTYe46A00I"
        genai.configure(api_key=API_KEY)
        
        # Create model with specified parameters
        generation_config = {
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_output_tokens": 2048,
        }
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Send the combined prompt directly
        response = model.generate_content(enhanced_prompt)
        
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def show_auth_ui():
    st.sidebar.header("👤 Account")
    
    if st.session_state['user_id']:
        st.sidebar.success(f"Logged in as: {st.session_state['user_email']}")
        if st.sidebar.button("Log Out"):
            st.session_state['user_id'] = None
            st.session_state['user_email'] = None
            st.session_state['saved_scripts'] = load_saved_scripts()
            st.rerun()
    else:
        tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Log In"):
                if email and password:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state['user_id'] = result
                        st.session_state['user_email'] = email
                        st.session_state['saved_scripts'] = load_scripts_from_cloud(result)
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result}")
                else:
                    st.error("Please enter both email and password.")
        
        with tab2:
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Register"):
                if email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        # Validate email format
                        if not is_valid_email(email):
                            st.error("Invalid email format. Please enter a valid email address.")
                        else:
                            success, result = register_user(email, password)
                            if success:
                                st.success("Registration successful! Please log in.")
                            else:
                                st.error(f"Registration failed: {result}")
                else:
                    st.error("Please fill in all fields.")

def main():
    st.set_page_config(page_title="AI Script Generator", layout="wide")
    
    # Initialize Firebase
    db, bucket = initialize_firebase()  # Ensure Firebase is initialized
    
    # Initialize session state
    initialize_session_state()
    
    # Show authentication UI in sidebar
    show_auth_ui()
    
    st.title("AI Script Generator")
    st.markdown("Create engaging YouTube scripts effortlessly with AI! 🎬✨")
    
    # User profile status
    if st.session_state['user_id']:
        st.info(f"Scripts will be saved to your cloud account: {st.session_state['user_email']}")
    else:
        st.warning("You're working in local mode. Log in to save scripts to the cloud.")

    # Tabs for writing and viewing saved scripts
    tab1, tab2, tab3 = st.tabs(["📜 Write Script", "💾 Saved Scripts", "⚙️ Advanced Settings"])

    with tab1:
        template_choice = st.selectbox("Choose a Script Template", ["Tutorial", "Product Review", "Storytelling", "Educational", "Vlog"])
        main_points = st.text_area("**What is your video about? 🎥**", placeholder="Describe your video idea...")
        
        col1, col2 = st.columns(2)
        with col1:
            tone_style = st.selectbox("**Select Tone & Style 🎭**", ["Casual", "Professional", "Humorous", "Inspirational", "Dramatic", "Educational"])
            video_length = st.selectbox("**Select Video Length ⏰**", ["Short (1-3 min)", "Medium (3-5 min)", "Long (5-10 min)"])
            language = st.selectbox("**Select Language 🌐**", ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese"])
        
        with col2:
            target_audience = st.multiselect("**Select Target Audience 🎯**", ["Beginners", "Tech Enthusiasts", "Entrepreneurs", "Students", "Professionals", "Hobbyists", "General Public"])
            seo_keywords = st.text_input("**Enter SEO Keywords (comma-separated)**")
            use_case = st.selectbox("**YouTube Script Use Case 📚**", ["Tutorials", "Product Reviews", "Explainer Videos", "Vlogs", "Motivational Speeches", "Comedy Skits", "Educational Content"])
        
        include_sections = st.multiselect("**Include Sections**", ["Introduction", "Main Content", "Call to Action", "FAQ Section", "Resources/Links"], default=["Introduction", "Main Content", "Call to Action"])

        # Show advanced prompt engineering options if enabled in settings
        show_advanced = st.session_state.get('show_advanced_options', False)
            
        advanced_options = {}
        if show_advanced:
            with st.expander("🧠 Advanced Prompt Controls"):
                col1, col2 = st.columns(2)
                
                with col1:
                    hook_style = st.selectbox("**Hook Style**", ["Question-based", "Shocking statistic", "Controversial statement", "Personal story", "Curiosity gap"])
                    storytelling_elements = st.selectbox("**Storytelling Elements**", ["Personal anecdotes", "Case studies", "Metaphors/analogies", "Character-driven", "Problem-solution"])
                    advanced_options["hook_style"] = hook_style
                    advanced_options["storytelling_elements"] = storytelling_elements
                    
                with col2:
                    transitions = st.selectbox("**Section Transitions**", ["Smooth/natural", "Question-based", "Summary-preview", "Visual cue suggestions"])
                    video_editing_cues = st.selectbox("**Video Editing Suggestions**", ["Basic cuts", "B-roll ideas", "Text overlays", "Visual effects", "None"])
                    advanced_options["transitions"] = transitions
                    advanced_options["video_editing_cues"] = video_editing_cues

        button_text = "Regenerate Script 📝" if st.session_state['script'] else "Write Script 📝"

        if st.button(button_text):
            with st.spinner("Generating your script... ⏳"):
                if not main_points:
                    st.error("🚫 Please provide a topic for the video.")
                else:
                    # Use enhanced prompt generation
                    enhanced_prompt = generate_enhanced_prompt(
                        main_points, tone_style, target_audience, video_length, 
                        language, seo_keywords, use_case, template_choice,
                        include_sections, advanced_options if show_advanced else None
                    )
                    
                    # Get model settings from session state if available
                    model_name = st.session_state.get('model_name', "gemini-1.5-flash-latest")
                    temperature = st.session_state.get('temperature', 0.7)
                    top_k = st.session_state.get('top_k', 20)
                    top_p = st.session_state.get('top_p', 0.9)
                    
                    st.session_state['script'] = generate_script_with_advanced_prompts(
                        enhanced_prompt, model_name, temperature, top_k, top_p
                    )
                    st.subheader("📜 Your YouTube Script")
                    st.write(st.session_state['script'])
                    
                    # Word count and duration statistics
                    word_count = len(st.session_state['script'].split())
                    est_duration = word_count // 150  # Approx 150 words per minute
                    st.text(f"Word Count: {word_count}, Estimated Duration: {est_duration} min")

        if st.session_state['script']:
            script_name = st.text_input("**Name Your Script 🏷️**", placeholder="Enter script name...")

            col1, col2, col3 = st.columns([3, 2, 3])

            with col1:
                format_choice = st.selectbox("**Download as**", ["TXT", "Markdown"])
                file_ext = "txt" if format_choice == "TXT" else "md"
                st.download_button(f"Download {format_choice}", st.session_state['script'], f"{script_name or 'script'}.{file_ext}")

            with col2:
                if st.button("Copy to Clipboard"):
                    pyperclip.copy(st.session_state['script'])
                    st.success("Copied to clipboard!")

            with col3:
                save_button_text = "Save to Cloud" if st.session_state['user_id'] else "Save Locally"
                if st.button(f"{save_button_text}"):
                    if script_name.strip():
                        save_script(script_name, st.session_state['script'])
                    else:
                        st.error("Please enter a name before saving.")

    with tab2:
        st.subheader("💾 Saved Scripts")
        
        # Add script search and filtering options for cloud users
        if st.session_state['user_id']:
            search_term = st.text_input("🔍 Search scripts", placeholder="Enter keyword...")
            
            # Refresh button to fetch latest scripts
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("🔄 Refresh"):
                    st.session_state['saved_scripts'] = load_scripts_from_cloud(st.session_state['user_id'])
                    st.success("Scripts refreshed!")
        
        if st.session_state['saved_scripts']:
            # Filter scripts if search term provided
            displayed_scripts = st.session_state['saved_scripts']
            if st.session_state.get('user_id') and 'search_term' in locals() and search_term:
                displayed_scripts = [s for s in displayed_scripts if search_term.lower() in s.get('name', '').lower() or 
                                    search_term.lower() in s.get('script', '').lower()]
            
            for idx, saved_script in enumerate(displayed_scripts):
                # Check if 'name' key exists, otherwise use a default name
                script_name = saved_script.get('name', 'Unnamed Script')
                with st.expander(f"{script_name}"):
                    st.write(saved_script.get('script', 'No script content available.'))
                    
                    col1, col2, col3 = st.columns([3, 3, 2])
                    
                    with col1:
                        # Load script into editor
                        if st.button(f"📝 Edit", key=f"edit_{idx}"):
                            st.session_state['script'] = saved_script.get('script', '')
                            st.rerun()
                    
                    with col2:
                        # Copy to clipboard
                        if st.button(f"📋 Copy", key=f"copy_{idx}"):
                            pyperclip.copy(saved_script.get('script', ''))
                            st.success("Copied to clipboard!")
                    
                    with col3:
                        # Delete script - handle both cloud and local
                        script_id = saved_script.get('id') if st.session_state['user_id'] else None
                        if st.button(f"❌ Delete", key=f"delete_{idx}"):
                            delete_script(idx, script_id)
                            st.rerun()
        else:
            st.write("No saved scripts yet. Write and save one!")
            
    with tab3:
        st.subheader("⚙️ Advanced Settings")
        
        st.toggle("Enable Advanced Prompt Engineering", key="show_advanced_options", value=True)
        
        with st.expander("🧠 View Current Prompt Templates"):
            templates = load_prompt_templates()
            for template_name, template_data in templates.items():
                st.subheader(template_name)
                st.write(f"**Structure:** {template_data['structure']}")
                st.write(f"**Example:** {template_data['example']}")
        
        with st.expander("📊 Model Parameters"):
            model_name = st.selectbox("AI Model", ["gemini-1.5-flash-latest", "gemini-pro", "gemini-1.5-pro-latest"], 
                                      index=0, key="model_name")
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, 
                                   help="Higher values make output more creative, lower values more deterministic",
                                   key="temperature")
            top_k = st.slider("Top-K", min_value=1, max_value=40, value=20, 
                             help="Limits token selection to K most likely tokens",
                             key="top_k")
            top_p = st.slider("Top-P", min_value=0.1, max_value=1.0, value=0.9, step=0.1, 
                              help="Model considers tokens with top_p probability mass",
                              key="top_p")
            
            if st.button("Save Model Settings"):
                st.success("Model settings saved!")
                
        # For cloud storage users only
        if st.session_state['user_id']:
            with st.expander("🔄 Cloud Storage Settings"):
                st.info("Your scripts are automatically synced to the cloud.")
                
                if st.button("Download All Scripts"):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_file = f"{temp_dir}/all_scripts.zip"
                        import zipfile
                        
                        with zipfile.ZipFile(zip_file, 'w') as zipf:
                            for script in st.session_state['saved_scripts']:
                                script_name = script.get('name', 'unnamed')
                                script_content = script.get('script', '')
                                
                                # Create a valid filename
                                safe_name = "".join([c if c.isalnum() or c in ['-', '_'] else '_' for c in script_name])
                                zipf.writestr(f"{safe_name}.txt", script_content)
                        
                        with open(zip_file, "rb") as f:
                            st.download_button(
                                "Download ZIP",
                                f,
                                f"all_scripts.zip",
                                "application/zip"
                            )

if __name__ == "__main__":
    main()
