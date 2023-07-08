# News bot

## Prerequisites
Before running the bot, you need to have a `data` and a `logs` folder in the root of your project with write access to it. Redis and PostgreSQL data and logs are kept there.

## Configuration
Rename `.env.example` to `.env` and provide your Telegram bot token, RapidAPI key, and password for Redis and PostgreSQL. You can also edit other values in this file.

## Running bot
`docker compose up`

## Debugging and logging
To debug set the `DEBUG` variable in your `.env` file to `True`. Logs are kept in the `logs` folder.

## Running tests
`pytest tests`

## Bot usage
* `/start` - starts or restarts the bot
* `/help` - displays help
* `/news` - gets news based on your search query and date range (one week selected). Then displays a summary of this news and the top 5 news in the week. You can click on any of these news and:
  * Get its summary
  * Read the full article
* `/history` - displays your search history. You can click on any of its items. Then a summary and the top 5 news are displayed. You can click on any of the top news and:
  * Get its summary
  * Read the full article
