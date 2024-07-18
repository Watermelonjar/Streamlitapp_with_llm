
# LLM App for Ollama

## Setup Instructions

### Prerequisites
- Ensure you have Python installed on your system.
- Install required packages using the `requirements.txt` file.

### Step 1: Install Required Packages
Install all the required Python packages by running:
```bash
pip install -r requirements.txt
```

### Step 2: Prepare Excel Sheets
Create a new folder named `Excel_sheets` in the project directory and place all your Excel files in this folder.

### Step 3 : Clean up the data 
Clean up the excel data by running `DataCleaner.py` to ready the data in the format of the app

### Step 4: Set Up Ollama
1. Download Ollama from the official [Ollama website](https://ollama.com/).
2. Install the Ollama Python package:
   ```bash
   pip install ollama
   ```
3. Pull the Gemma2 model:
   ```bash
   ollama pull gemma2
   ```
4. Ensure Ollama is running in the background.

### Step 5: Run the Streamlit App
Launch the Streamlit app by running the following command in your terminal:
```bash
streamlit run StreamlitApp.py
```
