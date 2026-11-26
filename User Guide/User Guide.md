# User Guide: Running the Data Visualization Dashboard

Step-by-step instructions for setting up and running the Mental Health Sentiment Analysis Dashboard on Windows, macOS, and Linux.

---

## For Windows Users

### Step 1: Download and Extract
1. Download the ZIP file of the project (or clone the repository).
2. Right-click on the ZIP folder, select **Extract All…**, and save it somewhere easy to find, such as `C:\DashboardProject\`.
3. Navigate to the `Dashboard` folder (`C:\DashboardProject\Mental-Health-Sentiment-Analysis\Dashboard`).
4. Verify that the folder contains the following files:
   ```text
   Dashboard/
   ├── Source Data/
   │   └── Combined Data.csv
   ├── app.py
   ├── design.py
   ├── functions.py
   └── visualizations.py
   ```

### Step 2: Open Command Prompt
1. Press **Start**, type `cmd`, and press **Enter**.
2. Navigate to the `Dashboard` folder:
   ```cmd
   cd C:\DashboardProject\Mental-Health-Sentiment-Analysis\Dashboard
   ```

### Step 3: Check Python Version
Run:
```cmd
python --version
```
If you see **Python 3.9 or higher**, continue. If not:
- Download the latest version from [python.org/downloads](https://www.python.org/downloads/).
- During installation, check **"Add Python to PATH"**.
- Verify again:
  ```cmd
  python --version
  ```

### Step 4: Install Required Libraries
Install all necessary packages:
```cmd
pip install dash dash-iconify plotly pandas textblob nltk
python -m textblob.download_corpora
```
*(Alternatively, run `pip install -r ..\requirements.txt` from the `Dashboard` folder.)*

This installs:
- **Dash & Dash Iconify & Plotly:** for the interactive web dashboard, icons, and charts
- **Pandas:** for data loading, cleaning, and manipulation
- **TextBlob & NLTK:** for sentiment analysis and stopword filtering
- **`re` (Regular Expressions):** built into Python, used for text pattern matching and cleaning (no separate installation needed)

### Step 5: Run the App
To start the dashboard, run:
```cmd
python app.py
```
When the terminal displays:
```text
Searching for 'Combined Data.csv'...
CLEANING DATA...
Preparing your Dashboard...
Launching Dashboard...
Dash is running on http://127.0.0.1:8050/
```
The dashboard will open automatically in your default browser within a few seconds. You can also open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) manually in your browser.

---

## For macOS Users

### Step 1: Download and Extract
1. Download the ZIP file of the project (or clone the repository).
2. Extract it to your Desktop, e.g., `~/Desktop/Mental-Health-Sentiment-Analysis`.
3. Verify the `Dashboard` folder contents:
   ```text
   Dashboard/
   ├── Source Data/
   │   └── Combined Data.csv
   ├── app.py
   ├── design.py
   ├── functions.py
   └── visualizations.py
   ```

### Step 2: Open Terminal
1. Press **Command + Space**, type `Terminal`, and press **Enter**.
2. Move to the `Dashboard` directory:
   ```bash
   cd ~/Desktop/Mental-Health-Sentiment-Analysis/Dashboard
   ```

### Step 3: Check Python Version
Run:
```bash
python3 --version
```
If you see **Python 3.9 or higher**, continue. If not, download and install the latest version from [python.org/downloads](https://www.python.org/downloads/), then verify again:
```bash
python3 --version
```

### Step 4: Install Required Libraries
```bash
pip3 install dash dash-iconify plotly pandas textblob nltk
python3 -m textblob.download_corpora
```
*(Alternatively, run `pip3 install -r ../requirements.txt` from the `Dashboard` folder.)*

This installs:
- **Dash & Dash Iconify & Plotly:** for the interactive web dashboard, icons, and charts
- **Pandas:** for data loading, cleaning, and manipulation
- **TextBlob & NLTK:** for sentiment analysis and stopword filtering
- **`re` (Regular Expressions):** built into Python, used for text pattern matching and cleaning (no separate installation needed)

### Step 5: Run the App
```bash
python3 app.py
```
You will see:
```text
Searching for 'Combined Data.csv'...
CLEANING DATA...
Preparing your Dashboard...
Launching Dashboard...
Dash is running on http://127.0.0.1:8050/
```
The dashboard will open automatically in your browser, or you can copy [http://127.0.0.1:8050/](http://127.0.0.1:8050/) and open it manually.

---

## For Linux (Ubuntu / Debian)

### Step 1: Update & Install Python
Open Terminal and run:
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```
Check your Python version:
```bash
python3 --version
```
If it is **3.9 or above**, continue.

### Step 2: Download and Extract
1. Copy the ZIP file to your Home or Desktop directory (or clone the repository).
2. Right-click the archive and select **Extract Here**.
3. Open the extracted folder and locate the `Dashboard` folder:
   ```text
   Dashboard/
   ├── Source Data/
   │   └── Combined Data.csv
   ├── app.py
   ├── design.py
   ├── functions.py
   └── visualizations.py
   ```

### Step 3: Navigate to the Project Folder
```bash
cd ~/Desktop/Mental-Health-Sentiment-Analysis/Dashboard
```

### Step 4: Install Required Libraries
```bash
pip3 install dash dash-iconify plotly pandas textblob nltk
python3 -m textblob.download_corpora
```
*(Alternatively, run `pip3 install -r ../requirements.txt` from the `Dashboard` folder.)*

This installs:
- **Dash & Dash Iconify & Plotly:** for creating the interactive web dashboard, icons, and charts
- **Pandas:** for data loading, cleaning, and manipulation
- **TextBlob & NLTK:** for performing sentiment analysis (polarity and subjectivity) and stopword filtering
- **`re` (Regular Expressions):** built into Python, used for text pattern matching and cleaning (no separate installation needed)

### Step 5: Run the Dashboard
```bash
python3 app.py
```
You will see:
```text
Searching for 'Combined Data.csv'...
CLEANING DATA...
Preparing your Dashboard...
Launching Dashboard...
Dash is running on http://127.0.0.1:8050/
```
Copy [http://127.0.0.1:8050/](http://127.0.0.1:8050/) into your browser if it does not open automatically, and the dashboard will appear within a few seconds.
