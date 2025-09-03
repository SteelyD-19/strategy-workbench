# OpenAI API Key Setup

## Quick Setup

1. **Edit the config file**: Open `config.env` and replace `your-openai-api-key-here` with your actual OpenAI API key
2. **Restart Streamlit**: The application will automatically load your API key

## File Structure

```
strategy-workbench/
├── config.env          # Your API key goes here
├── app.py              # Main Streamlit application
├── mentat-protocol/    # AI protocol implementation
└── setup_api_key.py    # Setup verification script
```

## Configuration File

The `config.env` file should contain:
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

## Verification

Run the setup script to verify your configuration:
```bash
python setup_api_key.py
```

## Security Notes

- Never commit your actual API key to version control
- The `config.env` file is already in `.gitignore` to prevent accidental commits
- Keep your API key secure and don't share it

## Troubleshooting

If you're still seeing the old responses:
1. Make sure you've replaced the placeholder in `config.env`
2. Restart the Streamlit application
3. Start a new project in the web interface
4. Run `python setup_api_key.py` to verify the setup
