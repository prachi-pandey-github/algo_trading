"""
API Keys Configuration Template

IMPORTANT: This is a template file. Create a copy named 'api_keys.py' and add your actual API credentials.

For security reasons, never commit your actual API keys to version control.
The api_keys.py file is already included in .gitignore to prevent accidental commits.
"""

# =============================================================================
# TELEGRAM BOT CONFIGURATION (Optional)
# =============================================================================
# To enable Telegram notifications, follow these steps:
# 1. Create a new bot by messaging @BotFather on Telegram
# 2. Get your bot token from BotFather
# 3. Get your chat ID by messaging @userinfobot
# 4. Uncomment and fill in the values below

# TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ1234567890"
# TELEGRAM_CHAT_ID = "123456789"

# =============================================================================
# EXAMPLE CONFIGURATION
# =============================================================================
# Here's what your api_keys.py file should look like:
"""
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "your_actual_bot_token_here"
TELEGRAM_CHAT_ID = "your_actual_chat_id_here"
"""

# =============================================================================
# DEFAULT VALUES (Used when Telegram is not configured)
# =============================================================================
# These default values will be used if Telegram is not configured
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

# =============================================================================
# FUTURE API CONFIGURATIONS
# =============================================================================
# Additional API configurations can be added here as the project expands:

# Alpha Vantage API (for enhanced data)
# ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key"

# IEX Cloud API (alternative data source)
# IEX_CLOUD_TOKEN = "your_iex_cloud_token"

# Quandl API (for economic data)
# QUANDL_API_KEY = "your_quandl_key"

# =============================================================================
# SETUP INSTRUCTIONS
# =============================================================================
print("""
⚠️  SETUP REQUIRED ⚠️

This is a template file. To set up your API keys:

1. Copy this file to 'api_keys.py' in the same directory
2. Edit 'api_keys.py' with your actual API credentials
3. Never commit 'api_keys.py' to version control

For Telegram notifications:
• Message @BotFather on Telegram to create a bot
• Get your bot token and chat ID
• Add them to your api_keys.py file

The trading system will work without Telegram, but you won't receive notifications.
""")
