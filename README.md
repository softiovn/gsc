Here's a comprehensive README.md file to guide users through the setup and running process:

# Search Analytics Pro Desktop App

A powerful desktop application built with Qt that connects to Google Search Console, analyzes website performance data, and provides AI-powered insights and suggestions using Google's Gemini API.

## Features

- 🔐 **Secure Authentication** - OAuth 2.0 integration with Google Search Console
- 📊 **Data Analytics** - Fetch and analyze search performance data
- 🤖 **AI-Powered Insights** - Get detailed analysis and recommendations using Gemini AI
- 💡 **Smart Suggestions** - Actionable SEO suggestions with implementation steps
- 🖥️ **Desktop Interface** - Native Qt-based desktop application
- 📈 **Performance Tracking** - Monitor clicks, impressions, CTR, and positions

## Prerequisites

Before running the application, ensure you have:

- **Python 3.8+** installed on your system
- A **Google account** with access to Google Search Console
- A **Google Gemini API key** (free tier available)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone or download** the project files to your local machine

2. **Make the run script executable** (Linux/macOS):

   ```bash
   chmod +x run.sh
   ```

3. **Run the setup script**:
   ```bash
   ./run.sh
   ```

The script will automatically:

- Check for Python 3
- Create a virtual environment
- Install all dependencies
- Launch the application

### Option 2: Manual Setup

If you prefer manual setup or the script doesn't work:

1. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment**:

   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     .venv\Scripts\activate
     ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` is not available:

   ```bash
   pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Configuration

### Step 1: Google Search Console Setup

1. **Enable Google Search Console API**:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the "Google Search Console API"
   - Create OAuth 2.0 credentials (Desktop application type)
   - Download the credentials file

2. **Save credentials**:
   - Create a `config` folder in the project directory
   - Save the downloaded credentials as `config/credentials.json`

### Step 2: Gemini API Setup

1. **Get Gemini API Key**:

   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the API key

2. **Configure in App**:
   - The app will prompt for the API key on first run
   - You can also set it later via Settings → Setup Gemini API Key

## Project Structure

```
search_analytics_app/
├── main.py                 # Application entry point
├── main_window.py          # Main window and UI setup
├── auth_manager.py         # Google OAuth authentication
├── gsc_client.py           # Google Search Console API client
├── gemini_analyzer.py      # Gemini AI integration for analysis
├── data_models.py          # Data structures and models
├── config_manager.py       # API key and configuration management
├── widgets/
│   └── dashboard_widget.py # Main dashboard UI component
├── config/
│   └── credentials.json    # Google OAuth credentials (create this)
├── requirements.txt        # Python dependencies
└── run.sh                 # Automated setup script
```

## Usage Guide

### 1. First Run Setup

1. **Launch the application** using the run script or manual method
2. **Authenticate with Google** when prompted
3. **Enter your Gemini API key** when requested

### 2. Fetching Data

1. **Select a website** from your Google Search Console properties
2. **Choose date range** for analysis (default: last 30 days)
3. **Click "Fetch Data"** to retrieve search analytics

### 3. AI Analysis

1. **Click "Analyze with AI"** after data is loaded
2. **Wait for analysis** - Gemini will process the data and provide insights
3. **Review results** in the analysis panel

### 4. Understanding Results

The analysis provides:

- **Summary**: Overall performance overview
- **Trends**: Key performance patterns and changes
- **Opportunities**: Areas for improvement and growth
- **Issues**: Problems and challenges identified
- **Recommendations**: Actionable steps to improve SEO
- **Suggestions**: Detailed implementation guides

## Troubleshooting

### Common Issues

1. **"Gemini API is not available"**

   - Check your API key in Settings
   - Ensure Gemini API is enabled in Google AI Studio
   - Verify internet connection

2. **Authentication Errors**

   - Ensure `config/credentials.json` exists
   - Check Google Search Console API is enabled
   - Verify you have access to the website in GSC

3. **No Data Available**

   - Ensure the selected website has search data in GSC
   - Check date range selection
   - Verify website verification in Google Search Console

4. **Module Import Errors**
   - Run `pip install -r requirements.txt` again
   - Ensure virtual environment is activated
   - Check Python version (requires 3.8+)

### Debug Mode

For detailed debugging information, check the console output for messages prefixed with:

- `🔧` - Initialization steps
- `✅` - Success messages
- `❌` - Error messages
- `📊` - Data processing
- `🎉` - Completion

## API Requirements

### Google Search Console API

- **Scope**: `https://www.googleapis.com/auth/webmasters.readonly`
- **Quota**: 10,000 requests per day (typically sufficient)

### Gemini API

- **Models**: gemini-1.5-pro, gemini-1.0-pro, or gemini-pro
- **Quota**: Free tier available, check current limits

## Data Privacy

- All authentication tokens are stored locally
- Google Search Console data is processed locally
- Gemini API requests contain anonymized performance data
- No personal data is stored on external servers

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure proper API configuration
4. Check console output for error messages

## License

This project is for educational and analytical purposes. Ensure compliance with Google API terms of service and data usage policies.

---

**Note**: This application requires access to your Google Search Console data. Only use with websites you own or have permission to analyze.
