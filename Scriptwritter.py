import os
import json
import streamlit as st
import google.generativeai as genai
import pyperclip

# Hardcoded API Key (Replace with environment variable in production)
API_KEY = "AIzaSyB8CLIP4vwf6QEYZJ5LsBrX3ZTYe46A00I"

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

def main():
    st.set_page_config(page_title="AI Script Generator", layout="wide")
    
    if 'saved_scripts' not in st.session_state:
        st.session_state['saved_scripts'] = load_saved_scripts()
    
    st.title("AI Script Generator")
    st.markdown("Create engaging YouTube scripts effortlessly with AI! 🎬✨")

    # Tabs for writing and viewing saved scripts
    tab1, tab2 = st.tabs(["📜 Write Script", "💾 Saved Scripts"])

    with tab1:
        template_choice = st.selectbox("Choose a Script Template", ["Custom", "Tutorial", "Product Review", "Storytelling"])
        main_points = st.text_area("**What is your video about? 🎥**", placeholder="Describe your video idea...")
        tone_style = st.selectbox("**Select Tone & Style 🎭**", ["Casual", "Professional", "Humorous", "Inspirational"])
        target_audience = st.multiselect("**Select Target Audience 🎯**", ["Beginners", "Tech Enthusiasts", "Entrepreneurs"])
        video_length = st.selectbox("**Select Video Length ⏰**", ["Short (1-3 min)", "Medium (3-5 min)", "Long (5-10 min)"])
        language = st.selectbox("**Select Language 🌐**", ["English", "Spanish", "French"])
        seo_keywords = st.text_input("**Enter SEO Keywords (comma-separated)**")
        use_case = st.selectbox("**YouTube Script Use Case 📚**", ["Tutorials", "Product Reviews", "Explainer Videos", "Vlogs", "Motivational Speeches", "Comedy Skits", "Educational Content"])
        
        include_intro = st.checkbox("Include Introduction", True)
        include_main = st.checkbox("Include Main Content", True)
        include_cta = st.checkbox("Include Call to Action", True)

        if 'script' not in st.session_state:
            st.session_state['script'] = ""

        button_text = "Regenerate Script 📝" if st.session_state['script'] else "Write Script 📝"

        if st.button(button_text):
            with st.spinner("Generating your script... ⏳"):
                if not main_points:
                    st.error("🚫 Please provide a topic for the video.")
                else:
                    st.session_state['script'] = generate_script(main_points, tone_style, target_audience, video_length, language, seo_keywords, use_case, include_intro, include_main, include_cta)
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
                        st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
        else:
            st.write("No saved scripts yet. Write and save one!")

def generate_script(main_points, tone_style, target_audience, video_length, language, seo_keywords, use_case, include_intro, include_main, include_cta):
    """Generates a YouTube script based on user input."""
    prompt = f"""
    Write a YouTube script in {language} for a {video_length} video about {main_points}.
    Tone: {tone_style}
    Target Audience: {', '.join(target_audience)}
    Keywords: {seo_keywords}
    Use Case: {use_case}

    Include the following sections:
    {'Introduction' if include_intro else ''}
    {'Main Content' if include_main else ''}
    {'Call to Action' if include_cta else ''}
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    main()