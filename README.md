# MAST Annotator Web

A flexible web application for analyzing multi-agent interaction traces using the MAST (Multi-Agent Systems Taxonomy) framework with LLM-as-a-Judge capabilities.

## Key Features

- **🔄 Flexible File Support**: Upload ANY file format (JSON, TXT, CSV, ZIP, etc.)
- **🤖 LLM-as-a-Judge**: Intelligent analysis using OpenAI GPT models
- **📊 MAST Taxonomy**: Comprehensive 15-failure-mode taxonomy across 3 categories
- **📈 Rich Visualizations**: Interactive charts and downloadable reports
- **🚀 Easy Deployment**: Docker support for local and cloud deployment

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Streamlit UI  │────▶│  FastAPI Backend │────▶│   LLM-as-Judge   │
│   (Port 9000)   │     │   (Port 3000)    │     │   (OpenAI API)   │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  MAST Taxonomy   │
                        │   (15 Modes)     │
                        └──────────────────┘
```

## Quick Start (Local Development)

1. Clone the repository and navigate to the project directory:
```bash
cd mast-annotator-web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (or leave MAST_FAKE_MODE=1 for testing)
```

4. Start both services with one command:
```bash
# Option 1: Using Python runner (recommended)
python run_app.py

# Option 2: Using shell script
./run_dev.sh

# Option 3: Manual startup (two terminals)
# Terminal 1:
PYTHONPATH=. uvicorn app.main:app --reload --port 3000

# Terminal 2:
PYTHONPATH=. streamlit run ui/streamlit_app.py --server.port 9000
```

5. Open your browser:
   - Streamlit UI: http://localhost:9000
   - API Documentation: http://localhost:3000/docs

## Docker Deployment

1. Build and run with Docker Compose:
```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here

# Start services
docker compose up -d
```

2. Access the services:
   - Streamlit UI: http://localhost:9000
   - API: http://localhost:3000/docs

## EC2 Deployment

1. Launch an EC2 instance (Ubuntu 22.04 recommended):
   - Instance type: t3.medium or larger
   - Security group: Open ports 3000, 9000, 22

2. SSH into your instance and install Docker:
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io -y
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

3. Clone the repository:
```bash
git clone <your-repo-url>
cd mast-annotator-web
```

4. Set environment variables and start services:
```bash
export OPENAI_API_KEY=your-key-here
docker compose up -d
```

5. Access your application:
   - Streamlit UI: http://<EC2-PUBLIC-IP>:9000
   - API: http://<EC2-PUBLIC-IP>:3000/docs

## API Usage Examples

### Upload and annotate traces:
```bash
curl -X POST "http://localhost:3000/annotate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@sample_trace.jsonl"
```

### Get annotation result:
```bash
curl -X GET "http://localhost:3000/result/{job_id}"
```

### Get taxonomy:
```bash
curl -X GET "http://localhost:3000/taxonomy"
```

### Health check:
```bash
curl -X GET "http://localhost:3000/health"
```

## How to Use

### 1. Upload Your Trace Files

The application accepts **ANY file format** - no need to worry about specific schemas:

- **📄 Text Files**: `.txt`, `.log`, `.md` - Raw conversation logs
- **📊 Structured Data**: `.json`, `.jsonl`, `.csv` - Any JSON or CSV format
- **📦 Archives**: `.zip` - Bulk upload multiple files
- **🔧 Custom Formats**: Any text-based format works!

### 2. Automatic Analysis

The LLM-as-a-Judge system will:
- **🔍 Parse** your files intelligently (no rigid schema required)
- **🧠 Analyze** content using MAST taxonomy knowledge
- **📋 Detect** failure modes across 15 categories
- **📊 Generate** distributions and statistics

### 3. View Results

Get comprehensive analysis with:
- **🎯 MAST Taxonomy Visualization**: Schematic figure showing failure modes positioned by conversation stage and colored by category
- **📈 Interactive Charts**: Failure mode distributions and categories
- **📋 Detailed Tables**: Per-trace summaries and failure counts
- **💾 Export Options**: Download results as CSV/JSON/PNG
- **🔍 Taxonomy Reference**: Built-in failure mode definitions

#### MAST Taxonomy Figure

The application generates a publication-quality schematic figure that visualizes:
- **Conversation Stages**: Pre-Execution, Execution, Post-Execution
- **Failure Categories**: Specification Issues, Inter-Agent Misalignment, Task Verification
- **Dynamic Percentages**: Real-time computed from your uploaded traces
- **Color-coded Bars**: Each failure mode positioned semantically by stage

![MAST Taxonomy Example](mast_taxonomy_demo.png)

### Example File Formats Supported

**Text/Log Files:**
```
Multi-Agent Conversation Log
User: Please solve this math problem
Agent1: I'll help with that calculation
Agent2: Let me double-check the result
...
```

**JSON (any structure):**
```json
{
  "conversation_id": "abc123",
  "turns": [
    {"speaker": "user", "message": "Hello"},
    {"speaker": "agent", "response": "Hi there"}
  ]
}
```

**CSV (flexible columns):**
```csv
timestamp,participant,message,metadata
2024-01-01,user,Hello,{}
2024-01-01,agent,Hi there,{}
```

**No specific format required** - the LLM understands context!

## MAST Taxonomy (15 Failure Modes)

The system analyzes traces for these failure modes across 3 categories:

### 📋 **Category 1: Specification Errors**
- **1.1** Disobey Task Specification
- **1.2** Disobey Role Specification  
- **1.3** Step Repetition
- **1.4** Loss of Conversation History
- **1.5** Unaware of Termination Conditions

### 🤝 **Category 2: Coordination Errors**
- **2.1** Conversation Reset
- **2.2** Fail to Ask for Clarification
- **2.3** Task Derailment
- **2.4** Information Withholding
- **2.5** Ignored Other Agent's Input
- **2.6** Action-Reasoning Mismatch

### 🔍 **Category 3: Verification Errors**
- **3.1** Premature Termination
- **3.2** No or Incorrect Verification
- **3.3** Weak Verification

## Configuration

### Environment Variables

```bash
# Required for real LLM analysis
OPENAI_API_KEY=your-openai-api-key-here

# Optional configuration
MAST_FAKE_MODE=1              # Use mock analysis (default for testing)
MAST_STORAGE_PATH=./data/jobs # Where to store results
MAST_MAX_FILE_MB=25          # File size limit
```

### Testing vs Production

**Testing Mode (Default):**
- Set `MAST_FAKE_MODE=1` in your `.env` file
- Uses mock analysis - no API calls or costs
- Perfect for development and demos

**Production Mode:**
- Set `MAST_FAKE_MODE=0` and provide `OPENAI_API_KEY`
- Uses real OpenAI GPT-4 for analysis
- Requires API credits

## Development

### Running Tests
```bash
pytest tests/
```

### Visualization Features

The MAST taxonomy visualization provides:

- **📊 Publication-Quality Figures**: Generate schematic diagrams matching academic paper standards
- **🎨 Dynamic Coloring**: Each category has distinct colors (purple, red, green)
- **📐 Semantic Positioning**: Failure modes positioned by conversation stage
- **🔢 Real-time Percentages**: Computed from your actual trace data
- **⚙️ Customizable**: Adjustable figure size, show/hide zero modes
- **💾 Export Ready**: Download as high-resolution PNG

#### Visualization Controls

- **Figure Size**: Choose from 800px, 1000px, or 1200px width
- **Zero Mode Display**: Toggle visibility of failure modes with 0% frequency
- **PNG Export**: Download publication-ready figures
- **Interactive Fallback**: Plotly charts if visualization fails

### Project Structure
```
mast-annotator-web/
├── app/                     # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── models.py           # Pydantic models
│   ├── annotator_service.py # LLM-as-a-Judge logic
│   ├── mast_figure.py      # MAST taxonomy visualization
│   ├── storage.py          # Persistence layer
│   ├── taxonomy.py         # MAST taxonomy definitions
│   └── settings.py         # Configuration
├── ui/                     # Streamlit frontend
│   └── streamlit_app.py   # Web interface
├── data/sample_traces/     # Example trace files
├── tests/                  # Test suite
├── mast_figure_demo.py     # Visualization demo script
└── docker-compose.yml      # Docker configuration
```

## License

MIT License - see LICENSE file for details.