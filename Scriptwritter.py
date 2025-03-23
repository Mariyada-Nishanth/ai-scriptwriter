import os
import json
import streamlit as st
import google.generativeai as genai
import pyperclip

# Hardcoded API Key (Replace with environment variable in production)
API_KEY = "your_api_key"

genai.configure(api_key=API_KEY)

# Load saved scripts
def load_saved_scripts():
    if os.path.exists("saved_scripts.json"):
        with open("saved_scripts.json", "r") as file:
            return [json.loads(line) for line in file]
    return []

# Save script
def save_script(script_name, script_text):
    if script_name.strip() and script_text.strip():
        script_data = {"name": script_name, "script": script_text}
        with open("saved_scripts.json", "a") as file:
            json.dump(script_data, file)
            file.write("\n")
        st.session_state['saved_scripts'].append(script_data)
        st.success("Script saved successfully!")
    else:
        st.error("Please enter a valid name and script before saving.")

# Delete script
def delete_script(index):
    saved_scripts = load_saved_scripts()
    if 0 <= index < len(saved_scripts):
        del saved_scripts[index]
        with open("saved_scripts.json", "w") as file:
            for script in saved_scripts:
                json.dump(script, file)
                file.write("\n")
        st.session_state['saved_scripts'] = saved_scripts

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

def main():
    st.set_page_config(page_title="AI Script Generator", layout="wide")
    
    if 'saved_scripts' not in st.session_state:
        st.session_state['saved_scripts'] = load_saved_scripts()
    
    st.title("AI Script Generator")
    st.markdown("Create engaging YouTube scripts effortlessly with AI! 🎬✨")

    # Tabs for writing and viewing saved scripts
    tab1, tab2, tab3 = st.tabs(["📜 Write Script", "💾 Saved Scripts", "⚙️ Advanced Settings"])

    with tab1:
        template_choice = st.selectbox("Choose a Script Template", ["Tutorial", "Product Review", "Storytelling", "Educational", "Vlog"])
        main_points = st.text_area("**What is your video about? 🎥**", placeholder="Describe your video idea...")
        tone_style = st.selectbox("**Select Tone & Style 🎭**", ["Casual", "Professional", "Humorous", "Inspirational", "Dramatic", "Educational"])
        target_audience = st.multiselect("**Select Target Audience 🎯**", ["Beginners", "Tech Enthusiasts", "Entrepreneurs", "Students", "Professionals", "Hobbyists", "General Public"])
        video_length = st.selectbox("**Select Video Length ⏰**", ["Short (1-3 min)", "Medium (3-5 min)", "Long (5-10 min)"])
        language = st.selectbox("**Select Language 🌐**", ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese"])
        seo_keywords = st.text_input("**Enter SEO Keywords (comma-separated)**")
        use_case = st.selectbox("**YouTube Script Use Case 📚**", ["Tutorials", "Product Reviews", "Explainer Videos", "Vlogs", "Motivational Speeches", "Comedy Skits", "Educational Content"])
        
        include_sections = st.multiselect("**Include Sections**", ["Introduction", "Main Content", "Call to Action", "FAQ Section", "Resources/Links"], default=["Introduction", "Main Content", "Call to Action"])

        # Show advanced prompt engineering options if enabled in settings
        show_advanced = False
        if 'show_advanced_options' in st.session_state:
            show_advanced = st.session_state['show_advanced_options']
            
        advanced_options = {}
        if show_advanced:
            st.subheader("🧠 Advanced Prompt Controls")
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

        if 'script' not in st.session_state:
            st.session_state['script'] = ""

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
                    st.text(f"Word Count: {len(st.session_state['script'].split())}, Estimated Duration: {len(st.session_state['script'].split()) // 150} min")

        if st.session_state['script']:
            script_name = st.text_input("**Name Your Script 🏷️**", placeholder="Enter script name...")

            col1, col2, col3 = st.columns([3, 2, 3])

            with col1:
                format_choice = st.selectbox("**Download as**", ["TXT", "Markdown"])
                file_ext = "txt" if format_choice == "TXT" else "md"
                st.download_button(f"Download {format_choice}", st.session_state['script'], f"{script_name}.{file_ext}")

            with col2:
                if st.button("Copy to Clipboard"):
                    pyperclip.copy(st.session_state['script'])
                    st.success("Copied to clipboard!")

            with col3:
                if st.button("Save Script for Future Reference"):
                    if script_name.strip():
                        save_script(script_name, st.session_state['script'])
                    else:
                        st.error("Please enter a name before saving.")

    with tab2:
        st.subheader("💾 Saved Scripts")
        if st.session_state['saved_scripts']:
            for idx, saved_script in enumerate(st.session_state['saved_scripts']):
                # Check if 'name' key exists, otherwise use a default name
                script_name = saved_script.get('name', 'Unnamed Script')
                with st.expander(f"{script_name}"):
                    st.write(saved_script.get('script', 'No script content available.'))
                    if st.button(f"❌ Delete '{script_name}'", key=f"delete_{idx}"):
                        delete_script(idx)
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

def generate_script_with_advanced_prompts(enhanced_prompt, model_name="gemini-1.5-flash-latest", 
                                          temperature=0.7, top_k=20, top_p=0.9):
    """Generates a YouTube script using advanced prompt engineering."""
    try:
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

if __name__ == "__main__":
    main()
