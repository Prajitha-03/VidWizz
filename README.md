# VIDWIZZ - Personalized Video Summarization and Chatbot Platform

VIDWIZZ is a web-based platform designed to automatically generate short summaries from long videos using Natural Language Processing (NLP) techniques. It also features a personalized chatbot to help users understand video content more interactively.

## 🚀 Project Overview

With the rising consumption of video content, viewers often find it time-consuming to watch lengthy videos. VIDWIZZ solves this by:
- Generating short, meaningful summaries.
- Allowing user interaction via a chatbot trained on video transcripts.
- Improving accessibility and learning efficiency.

## 🧠 Features

- 📼 Video Uploading and Processing
- ✂️ Scene Detection and Segmentation
- 📝 Transcript Generation (via Whisper API)
- 🔍 Summarization using BART (Transformer model)
- 🤖 Personalized Chatbot using LangChain and OpenAI GPT
- 🧠 Memory integration with ChromaDB for context-aware conversations

## 🛠️ Tech Stack

- **Frontend**: React.js, Tailwind CSS
- **Backend**: Flask, Python
- **NLP & ML**: Hugging Face Transformers, OpenAI APIs, Whisper
- **Database**: SQLite (for metadata), ChromaDB (for vector storage)
- **Others**: LangChain, MoviePy, FFmpeg, Git

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/vidwizz.git
   cd vidwizz
