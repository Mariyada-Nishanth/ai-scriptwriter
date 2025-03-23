# AI Script Generator 🎬✨

Welcome to the **AI Script Generator**, a powerful tool designed to help you create engaging YouTube scripts effortlessly using AI! Whether you're creating tutorials, product reviews, storytelling videos, or any other type of content, this app has got you covered. 🚀

---

## Features 🌟

- **Customizable Script Templates**: Choose from templates like **Tutorial**, **Product Review**, **Storytelling**, **Educational**, or **Vlog**—or create your own custom script. 🎨  
- **Tone & Style Selection**: Tailor your script's tone with options like **Casual**, **Professional**, **Humorous**, **Inspirational**, or **Dramatic**. 🎭  
- **Target Audience**: Specify your audience (e.g., **Beginners**, **Tech Enthusiasts**, **Entrepreneurs**, **Students**, or **General Public**). 🎯  
- **Video Length**: Generate scripts for **Short (1-3 min)**, **Medium (3-5 min)**, or **Long (5-10 min)** videos. ⏰  
- **Multilingual Support**: Create scripts in **English**, **Spanish**, **French**, **German**, **Italian**, **Portuguese**, or **Japanese**. 🌐  
- **SEO Optimization**: Add SEO keywords to make your video more discoverable on YouTube. 🔍  
- **Advanced Prompt Engineering**: Fine-tune your script with options like **Hook Style**, **Storytelling Elements**, **Transitions**, and **Video Editing Cues**. 🧠  
- **Save & Manage Scripts**: Save your scripts to the **cloud** or **locally**, and manage them with ease. 💾  
- **Download & Copy**: Download scripts as **TXT** or **Markdown** files, or copy them to your clipboard with one click. 📥📋  
- **Cloud Sync**: Securely store and access your scripts from anywhere with **Firebase Cloud Storage**. ☁️  
- **Bulk Download**: Download all your scripts as a **ZIP file** for easy backup or offline use. 📦  
- **Real-Time Editing**: Edit and regenerate scripts on the fly for quick adjustments. ✏️  
- **User Authentication**: Log in to save scripts to your personal cloud account or use the app in **local mode**. 👤  
- **Search & Filter**: Easily find your saved scripts with a powerful search and filter feature. 🔍  
- **Model Customization**: Adjust AI parameters like **Temperature**, **Top-K**, and **Top-P** for more control over script generation. ⚙️  
- **Two-Column Format**: Scripts are generated in a **two-column format** with **[VISUAL]** and **[NARRATION]** sections for easy video production. 🎬  
- **Timestamps**: Automatically includes **timestamps** every 30 seconds for better video planning. ⏱️  
- **Call to Action**: Add **CTA sections** to engage your audience and drive action. 📢  
- **FAQ & Resources**: Include **FAQ sections** and **resource links** for a more comprehensive video. 📚  

---

## How It Works 🛠️

1. **Choose a Template**: Select a script template or go with a custom one.
2. **Describe Your Video**: Enter the main points of your video idea. 🎥
3. **Customize Settings**: Set the tone, target audience, video length, language, and SEO keywords.
4. **Generate Script**: Click "Write Script" and let the AI do the magic! ✨
5. **Save or Download**: Save your script for later or download it in your preferred format. 💾📥

---

Here’s the technology stack used to build this project:

- **Frontend**: 
  - 🎨 **Streamlit** - For building the interactive web app.
- **Backend**:
  - 🐍 **Python** - The core programming language.
  - 🤖 **Google Generative AI API** - For generating scripts using AI.
- **Utilities**:
  - 📋 **Pyperclip** - For copying text to the clipboard.
  - 📂 **JSON** - For saving and loading scripts.
  - 🗂️ **OS** - For file handling and path management.

---

## Installation 🚀

To run this app locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mariyada-Nishanth/ai-scriptwriter
   cd ai-script-generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Key**:
   - Replace the `API_KEY` in the script with your Google Generative AI API key.
   - Alternatively, set the API key as an environment variable:
     ```bash
     export GOOGLE_API_KEY="your_api_key_here"
     ```

4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

5. **Open in Browser**:
   - The app will open in your default browser at `http://localhost:8501`.

---

## Usage 🖥️

1. **Write Script Tab**:
   - Fill in the details about your video.
   - Click "Write Script" to generate the script.
   - Save, download, or copy the script to your clipboard.

2. **Saved Scripts Tab**:
   - View all your saved scripts.
   - Delete scripts you no longer need.

---

## Screenshot

![image](https://github.com/user-attachments/assets/b682853f-922a-43f7-9dc3-d4641c565fae)
![image](https://github.com/user-attachments/assets/ece90bd9-8548-4956-805b-c61bf5eff97c)
![image](https://github.com/user-attachments/assets/37f2b37a-9f4a-4242-aa14-bb9c7f135ed7)
![image](https://github.com/user-attachments/assets/3acc2094-174c-4137-bb68-b5472c6e9266)
![image](https://github.com/user-attachments/assets/a52c7753-4231-4df2-b116-7b5201b19984)
![image](https://github.com/user-attachments/assets/68f0c41f-36c0-4938-8886-ec2ba92a6afd)
![image](https://github.com/user-attachments/assets/68c20b3e-aefd-4dba-9da7-61701897f5b4)
![image](https://github.com/user-attachments/assets/f292bcf5-a54b-4e35-8e78-09158f6709f1)








## Example Prompts 💡

- **Tutorial**: "How to set up a home theater system."
- **Product Review**: "Review of the latest iPhone model."
- **Storytelling**: "A day in the life of a software engineer."

---

## Acknowledgments 🙏

- Thanks to **Google Generative AI** for providing the AI model. 🤖
- Built with ❤️ using **Streamlit** and **Python**.

---
