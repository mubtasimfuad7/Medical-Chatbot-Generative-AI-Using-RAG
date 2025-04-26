# Local RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that provides information using local LLM and vector search.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Internet connection for downloading dependencies and models

### Setup on Linux/macOS
1. Clone or download this repository
2. Open a terminal in the repository directory
3. Run the setup script:
   ```
   chmod +x setup_mchatbot.sh
   ./setup_mchatbot.sh
   ```
4. Download the LLM model file (Qwen2-1.5B-Instruct.Q8_0.gguf) and place it in the `models/model_files` directory
   - You can download it from [https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF](https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF)

### Setup on Windows
1. Clone or download this repository
2. Download the LLM model file (Qwen2-1.5B-Instruct.Q8_0.gguf) and place it in the `models\model_files` directory
   - You can download it from [https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF](https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF)

### Manual Setup
If you prefer to set up the environment manually:
1. Create a virtual environment:
   ```
   python -m venv mchatbot
   ```
2. Activate the environment using the environment.yaml file
3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
4. Create the model directory and download the model:
   ```
   mkdir -p models/model_files
   ```
5. Download the LLM model file (Qwen2-1.5B-Instruct.Q8_0.gguf) and place it in the `models/model_files` directory

### Using Conda Environment
If you prefer to use Conda for environment management:

1. Install Miniconda or Anaconda if you haven't already
   - Download from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

2. Create a new environment from the provided environment.yml file:
   ```
   conda env create -f environment.yml
   ```

3. Activate the conda environment:
   ```
   conda activate mchatbot
   ```

4. Create the model directory and download the model:
   ```
   mkdir -p models/model_files
   ```

5. Download the LLM model file (Qwen2-1.5B-Instruct.Q8_0.gguf) and place it in the `models/model_files` directory

## Environment Variables

**IMPORTANT**: This application requires certain environment variables to run properly on any machine. The best practice is to create a `.env` file in the root directory with the following variables:

```
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=us-east-1
LLM_DEVICE=cpu  # or 'gpu' if you have compatible hardware
EMBEDDING_DEVICE=cpu
```

You can create this file by running:
```
echo "PINECONE_API_KEY=your_api_key_here" > .env
echo "PINECONE_ENVIRONMENT=us-east-1" >> .env
echo "LLM_DEVICE=cpu" >> .env
echo "EMBEDDING_DEVICE=cpu" >> .env
```

> **Note**: You must obtain a valid Pinecone API key from [Pinecone](https://www.pinecone.io/) for the vector search functionality to work.

## Running the Application

1. Activate the virtual environment if not already activated:
   - On Linux/macOS: `source mchatbot/bin/activate`
   - On Windows: `mchatbot\Scripts\activate.bat`
2. Run the application:
   ```
   python app.py
   ```
3. Open a web browser and go to:
   ```
   http://localhost:8080
   ```

## Configuration

You can configure the application by:
1. Setting environment variables (recommended for sensitive data like API keys)
2. Modifying the `config.py` file (for non-sensitive settings)

Key configuration options:
- `LLM_MODEL_NAME`: Name of the LLM model to use
- `PINECONE_API_KEY`: API key for Pinecone (set via environment variable)
- `PINECONE_ENV`: Pinecone environment to use
- `LLM_DEVICE`: Set to "cpu" or "gpu" depending on your hardware

## Troubleshooting

If you encounter issues:

1. **"System is currently in maintenance mode"**:
   - Check that you have set the PINECONE_API_KEY environment variable
   - Verify that the LLM model file exists in models/model_files

2. **Application works on one machine but not another**:
   - Ensure the correct environment variables are set on all machines
   - Check that the model file is present in the correct location
   - Verify Python and package versions match

3. **General issues**:
   - Check the logs at `logs/medicalbot.log`
   - Ensure all dependencies are installed correctly
   - If using GPUs, ensure you have appropriate CUDA drivers installed

## Logs and Debugging

The application stores logs in the `logs/medicalbot.log` file. Check these logs for detailed error messages if you experience issues.

You can also check the application status by visiting:
```
http://localhost:8080/api/system/status
```
