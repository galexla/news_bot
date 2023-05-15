# News bot

## Prerequisites
Before running you need to have `data` directory with write access in the root of your project to keep Redis and PostgreSQL data there.

## Running bot
`docker compose up`

## Debugging
To debug set DEBUG variable in your .env file to True

## Bot usage

* /news - gets news and allows to analyze them further:
  * Get summary text
  * Get 5 most important news:
    * Get emotions of a news article
    * Read full article on the Web
* /help - displays help
