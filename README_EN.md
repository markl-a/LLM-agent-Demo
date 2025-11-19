# 🤖 LLM Agent & RAG Complete Practical Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0+-green.svg)](https://python.langchain.com/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.11.0+-orange.svg)](https://www.llamaindex.ai/)

> A comprehensive LLM Agent framework learning and practice project, covering mainstream frameworks like LangChain, LlamaIndex, AutoGen, CrewAI, and practical applications including RAG, multimodal processing, and code analysis.

![Cover](cover.png)

## 📚 Table of Contents

- [Project Introduction](#-project-introduction)
- [Key Features](#-key-features)
- [Directory Structure](#-directory-structure)
- [Quick Start](#-quick-start)
- [Learning Paths](#-learning-paths)
- [Framework Comparison](#-framework-comparison)
- [Real-World Use Cases](#-real-world-use-cases)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Project Introduction

This project is a comprehensive LLM Agent and RAG (Retrieval-Augmented Generation) learning resource repository designed to help developers:

- **Deep Understanding** of multiple mainstream LLM Agent frameworks' principles and usage
- **Master RAG** technology with various implementation approaches
- **Learn Multimodal** LLM application development
- **Analyze Open Source Projects** and their internal mechanisms
- **Practice Real-World Scenarios** with AI Agent applications

### Supported Frameworks and Technologies

| Framework/Technology | Version | Completion | Description |
|---------------------|---------|------------|-------------|
| **LangChain** | 0.3.0+ | ✅ Complete | 11 detailed tutorials covering RAG, Agent, LCEL, etc. |
| **LangGraph** | 0.2.30+ | ✅ Complete | State graph agent building framework |
| **LlamaIndex** | 0.11.0+ | 🆕 New | Data indexing and query framework |
| **AutoGen** | 0.2.0+ | 🆕 New | Microsoft's multi-agent conversation framework |
| **CrewAI** | 0.80.0+ | 🆕 New | Role-playing multi-agent framework |
| **MetaGPT** | Latest | 🆕 New | Software company simulation framework |
| **RAG Technology** | - | ✅ Complete | Basic RAG, multimodal RAG, advanced retrieval |
| **Vector Databases** | - | ✅ Complete | Chroma, FAISS, Pinecone, Qdrant |

## ✨ Key Features

### 1. Complete Learning Path
- 📖 Systematic tutorials from basics to advanced
- 💡 Rich code examples with detailed annotations
- 🎓 Real project case studies

### 2. Multi-Framework Comparison
- 🔍 In-depth analysis of framework pros and cons
- 📊 Selection guides and comparison tables
- 🛠️ Best practices from real-world implementations

### 3. Open Source Project Analysis
- 🔬 Deep dive into Open Hands, UFO, PCAgent, and other projects
- 📐 Detailed architecture and flow diagrams
- 💻 Source code interpretation and implementation principles

### 4. Real-World Applications
- 📧 Email auto-reply system
- 🗣️ Intelligent chatbot
- 🔍 SQL query agent
- 📊 Sales outreach automation

## 📂 Directory Structure

```
LLM-agent-Demo/
│
├── 1.從AI到LLM基礎/              # 🆕 AI/ML/DL/LLM fundamentals tutorial
│   ├── 0.AI基礎概念.md
│   ├── 1.機器學習基礎.md
│   ├── 2.深度學習基礎.md
│   ├── 3.Transformer架構詳解.md
│   ├── 4.LLM基礎知識.md
│   ├── 5.提示工程指南.md
│   └── README.md
│
├── 1.LangchainDemos/              # LangChain tutorials
│   ├── 0.簡單的RAG_範例.ipynb
│   ├── 1.langchain官網使用範例：RAG問答/
│   ├── 2.向量儲存與檢索器.ipynb
│   ├── 3.使用_LCEL_建立簡單的_LLM_應用.ipynb
│   ├── 4.建構一個聊天機器人.ipynb
│   ├── 5.使用langgraph建立Agent.ipynb
│   ├── 6.code_understanding_ipynb繁中翻譯.ipynb
│   ├── 7.結合_RAG_與自我修正的程式碼生成.ipynb
│   ├── 8.LongWriter_粗略了解.md
│   └── 9.sql_agent_中文化.ipynb
│
├── 2.Multi_modal_RAG/             # Multimodal RAG tutorials
│   ├── langchain_cookbook_Multi_modal_RAG.ipynb
│   └── cj/                        # Sample data
│
├── 3.程式碼解析/                   # Open source project code analysis
│   ├── 1-open_hands_程式碼解析.md
│   ├── 2-open-hands-docker交互流程.md
│   ├── Cline.md                   # 🆕 New
│   ├── PCAgent架構流程.md
│   ├── RDAgent.md
│   ├── RDAgent-通用模型.md
│   ├── UFO.md
│   └── OepnAdapt.md
│
├── 4.RPA_LLM/                     # RPA and LLM integration research
│   └── survey.md
│
├── 5.demo-sales-outreach-automation-langgraph/  # Sales automation case
│   ├── README.md
│   └── setup_script.py
│
├── 6.LlamaIndex/                  # 🆕 LlamaIndex tutorials
│   ├── 0.快速開始.ipynb
│   ├── 1.數據加載與索引.ipynb
│   ├── 2.查詢引擎.ipynb
│   ├── 3.Chat_Engine聊天引擎.ipynb
│   └── README.md
│
├── 7.AutoGen/                     # 🆕 AutoGen tutorials
│   ├── 0.基礎對話.ipynb
│   ├── 1.多Agent協作.ipynb
│   ├── 2.程式碼執行Agent.ipynb
│   └── README.md
│
├── 8.CrewAI/                      # 🆕 CrewAI tutorials
│   ├── 0.快速開始.ipynb
│   ├── 1.角色和任務.ipynb
│   ├── 2.實際案例.ipynb
│   └── README.md
│
├── 9.MetaGPT/                     # 🆕 MetaGPT tutorials
│   ├── 0.基礎概念.ipynb
│   ├── 1.軟體開發流程.ipynb
│   └── README.md
│
├── 10.框架對比與選擇指南/          # 🆕 Framework comparison
│   ├── 框架對比表.md
│   ├── 選擇指南.md
│   └── 最佳實踐.md
│
├── 11.實際應用案例/                # 🆕 Additional application cases
│   ├── 客服機器人/
│   ├── 文檔問答系統/
│   ├── 智能搜索引擎/
│   └── 程式碼助手/
│
├── requirements.txt               # Project dependencies
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # 🆕 Docker support
├── docker-compose.yml             # 🆕 Container orchestration
├── LICENSE                        # MIT license
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip or conda package manager
- (Optional) Docker and Docker Compose

### Installation

#### Method 1: Using Virtual Environment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
# Edit the .env file and add your API Keys
```

#### Method 2: Using Docker (Recommended for Production)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo

# 2. Start with Docker Compose
docker-compose up -d

# 3. Access Jupyter Lab
# Open http://localhost:8888 in your browser
```

### API Keys Configuration

Create a `.env` file and add the following:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google Gemini
GOOGLE_API_KEY=your_google_api_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key

# Groq
GROQ_API_KEY=your_groq_api_key

# Vector Databases (Optional)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment

# Other Services (Optional)
SERPER_API_KEY=your_serper_api_key
```

### Running Examples

```bash
# Start Jupyter Lab
jupyter lab

# Or start Jupyter Notebook
jupyter notebook

# Then open any .ipynb file to start learning
```

## 🎓 Learning Paths

### Complete Beginner Path (Week 0-4) 🆕

**Stage 0: Fundamentals (1-2 weeks)**
- `1.從AI到LLM基礎/` - Complete AI/ML/DL/LLM fundamentals tutorial
  - Starting from AI concepts, progressively diving into LLM
  - Includes theoretical explanations and code practice
  - Suitable for complete beginners with zero background

**Stage 1: Framework Introduction (3-4 weeks)**
- Enter LangChain practical learning

### Learners with Background (Week 1-2)

1. **LangChain Basics**
   - `1.LangchainDemos/0.簡單的RAG_範例.ipynb`
   - `1.LangchainDemos/2.向量儲存與檢索器.ipynb`
   - `1.LangchainDemos/3.使用_LCEL_建立簡單的_LLM_應用.ipynb`

2. **RAG Technology**
   - `1.LangchainDemos/1.langchain官網使用範例：RAG問答/`

3. **Basic Agents**
   - `1.LangchainDemos/4.建構一個聊天機器人.ipynb`

### Intermediate Path (Week 3-4)

1. **LangGraph Agent**
   - `1.LangchainDemos/5.使用langgraph建立Agent.ipynb`

2. **Multimodal RAG**
   - `2.Multi_modal_RAG/langchain_cookbook_Multi_modal_RAG.ipynb`

3. **LlamaIndex**
   - All tutorials in `6.LlamaIndex/` directory

4. **Practical Applications**
   - `1.LangchainDemos/9.sql_agent_中文化.ipynb`
   - `1.LangchainDemos/7.結合_RAG_與自我修正的程式碼生成.ipynb`

### Advanced Path (Week 5-6)

1. **Multi-Agent Systems**
   - All tutorials in `7.AutoGen/` directory
   - All tutorials in `8.CrewAI/` directory
   - All tutorials in `9.MetaGPT/` directory

2. **Code Analysis**
   - All files in `3.程式碼解析/` directory
   - Understanding open source project architecture and implementation

3. **Real Projects**
   - `5.demo-sales-outreach-automation-langgraph/`
   - Various subdirectories in `11.實際應用案例/`

## 🔍 Framework Comparison

For detailed comparison, see `10.框架對比與選擇指南/框架對比表.md`

### Quick Comparison

| Framework | Use Case | Complexity | Community | Learning Curve |
|-----------|----------|------------|-----------|----------------|
| **LangChain** | General LLM apps | Medium | ⭐⭐⭐⭐⭐ | Medium |
| **LlamaIndex** | Data indexing & query | Low-Medium | ⭐⭐⭐⭐ | Lower |
| **AutoGen** | Multi-agent dialogue | Medium-High | ⭐⭐⭐⭐ | Medium |
| **CrewAI** | Role-playing agents | Medium | ⭐⭐⭐ | Lower |
| **MetaGPT** | Software dev process | High | ⭐⭐⭐ | Higher |
| **LangGraph** | Complex state management | Medium-High | ⭐⭐⭐⭐ | Medium |

### Selection Recommendations

- **RAG Applications**: LangChain or LlamaIndex
- **Chatbots**: LangChain + LangGraph
- **Multi-Agent Collaboration**: AutoGen or CrewAI
- **Software Development**: MetaGPT
- **Complex Workflows**: LangGraph

## 💼 Real-World Use Cases

### 1. Email Auto-Reply System
- Location: `1.LangchainDemos/yt_email_reply_llama3_crewai_groq.ipynb`
- Tech Stack: CrewAI + Groq
- Features: Automatically analyze YouTube comments and generate professional replies

### 2. SQL Query Agent
- Location: `1.LangchainDemos/9.sql_agent_中文化.ipynb`
- Tech Stack: LangChain + SQL Database
- Features: Natural language to SQL query conversion

### 3. Sales Outreach Automation
- Location: `5.demo-sales-outreach-automation-langgraph/`
- Tech Stack: LangGraph + Multiple APIs
- Features: Automated sales process management

### 4. Code Understanding & Generation
- Location: `1.LangchainDemos/6.code_understanding_ipynb繁中翻譯.ipynb`
- Tech Stack: LangChain + RAG
- Features: Code analysis and intelligent generation

## 🆕 Latest Updates for 2025

This project has been updated to the latest 2025 version, including:

- ✅ LangChain 0.3.0+ new features
- ✅ LangGraph 0.2.30+ state management
- ✅ LlamaIndex 0.11.0+ complete tutorials
- ✅ AutoGen 0.2.0+ multi-agent systems
- ✅ CrewAI 0.80.0+ role-playing framework
- ✅ Latest vector database integrations
- ✅ Docker containerization support
- ✅ Complete dependency management

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Areas

- 📝 Add new tutorials or examples
- 🐛 Fix bugs or improve existing code
- 📚 Improve documentation
- 🌐 Add translations in other languages
- 💡 Propose new ideas or suggestions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgements

- [LangChain](https://python.langchain.com/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [CrewAI](https://www.crewai.io/)
- [MetaGPT](https://github.com/geekan/MetaGPT)
- All contributors in the open source community

## 📞 Contact

- Issue Reports: [GitHub Issues](https://github.com/yourusername/LLM-agent-Demo/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/LLM-agent-Demo/discussions)

## 🗺️ Roadmap

- [x] Complete LangChain tutorials
- [x] LangGraph agent system
- [x] Multimodal RAG
- [x] LlamaIndex tutorials
- [x] AutoGen tutorials
- [x] CrewAI tutorials
- [x] MetaGPT tutorials
- [x] Framework comparison guide
- [ ] More real-world application cases
- [ ] Video tutorials
- [ ] English version
- [ ] Online interactive tutorials

---

⭐ If this project helps you, please give us a Star!

📖 Continuously updating... Last update: 2025-01-14
