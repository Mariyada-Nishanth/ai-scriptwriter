# AI Script Generator 🎬✨

Welcome to the **AI Script Generator**, a powerful tool designed to help you create engaging YouTube scripts effortlessly using AI! Whether you're creating tutorials, product reviews, storytelling videos, or any other type of content, this app has got you covered. 🚀

---

## Features 🌟

- **Customizable Script Templates**: Choose from templates like Tutorial, Product Review, Storytelling, or create your own custom script. 🎨
- **Tone & Style Selection**: Tailor your script's tone with options like Casual, Professional, Humorous, or Inspirational. 🎭
- **Target Audience**: Specify your audience (e.g., Beginners, Tech Enthusiasts, Entrepreneurs). 🎯
- **Video Length**: Generate scripts for Short (1-3 min), Medium (3-5 min), or Long (5-10 min) videos. ⏰
- **Multilingual Support**: Create scripts in English, Spanish, or French. 🌐
- **SEO Optimization**: Add SEO keywords to make your video more discoverable. 🔍
- **Save & Manage Scripts**: Save your scripts for future reference and manage them easily. 💾
- **Download & Copy**: Download scripts as TXT or Markdown files, or copy them to your clipboard. 📥📋

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

![image](https://github.com/user-attachments/assets/808b041f-f90a-426c-987f-7a3174631ba7)
![image](https://github.com/user-attachments/assets/71b6b7ac-fde2-4cde-a156-34f75919f178)
![image](https://github.com/user-attachments/assets/a6417eba-5b72-4794-8fb4-6f359f646286)
![image](https://github.com/user-attachments/assets/c7835a3e-d544-4b65-8437-6bd771ceeb23)





## Example Prompts 💡

- **Tutorial**: "How to set up a home theater system."
- **Product Review**: "Review of the latest iPhone model."
- **Storytelling**: "A day in the life of a software engineer."

---

## Acknowledgments 🙏

- Thanks to **Google Generative AI** for providing the AI model. 🤖
- Built with ❤️ using **Streamlit** and **Python**.

---
