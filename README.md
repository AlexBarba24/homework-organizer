## Homework Organizer

An Electron application designed to help students keep track of homework assignments and exams. Students can upload syllabus pdf files and the program will read through the file using OpenAI and will automatically detects all of key events and add them t oyour google calendar.


## Usage

=======
## Project Setup

### Install

```bash
# Install Node.js dependencies
$ yarn

# Setup Python virtual environment and install dependencies
# On macOS/Linux:
$ yarn setup:python

# On Windows:
$ yarn setup:python:win

# Setup Google OAuth credentials (optional - for calendar integration)
$ yarn setup:credentials
# Then edit src/python/credentials.json with your Google OAuth credentials
```

**Note:** You'll also need to install Tesseract OCR:
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`
- **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Google Calendar Integration Setup

To enable Google Calendar integration:

1. **Get Google OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create or select a project
   - Enable the Google Calendar API
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials file

2. **Add Credentials to Project:**
   - Copy `src/python/credentials.json.example` to `src/python/credentials.json`
   - Replace the placeholder values with your actual credentials from the downloaded file
   - Or use environment variables (see below)

3. **Alternative: Use Environment Variables (for CI/CD):**
   ```bash
   export GOOGLE_CLIENT_ID="your-client-id"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   export GOOGLE_REDIRECT_URI="http://localhost"
   ```

**Security Note:** `credentials.json` is in `.gitignore` and should never be committed to version control. For public releases, use environment variables or inject credentials during the build process.

### Development

```bash
$ yarn dev
```

### Build

```bash
# For windows
$ yarn build:win

# For macOS
$ yarn build:mac

# For Linux
$ yarn build:linux
```

## Python Dependencies

Python dependencies are managed via `requirements.txt`. The virtual environment is automatically detected when running the app. OpenCV is optional - the app will use PIL/Pillow for image processing if OpenCV is not available.

## Building for Distribution

### Building with Credentials

For building releases with Google Calendar integration:

**Option 1: Environment Variables**
```bash
GOOGLE_CLIENT_ID="your-id" GOOGLE_CLIENT_SECRET="your-secret" yarn build:mac
```

**Option 2: Include credentials.json**
- Place `credentials.json` in `src/python/` before building
- It will be included in the build (ensure it's not in .gitignore for this build)
- **Note:** Only do this for private/internal builds, not for open source releases

### Building without Credentials

The app will work without credentials, but Google Calendar features will be disabled. Users can add their own `credentials.json` after installation.

## Development

For development, you can either:
- Use `credentials.json` file (recommended for local dev)
- Use environment variables
- Skip credentials (calendar features won't work)
>>>>>>> 767fb28 (Improved UI)
