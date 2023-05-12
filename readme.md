# News bot

## Prerequisites
Before running you need to have `data` directory with write access in root of your project to keep Redis and PostgreSQL data there.

## Running bot
`docker compose up`

## Debugging
To debug set DEBUG variable in your .env file to True

## Bot usage

* /news - gets news and allows to analyze them further:
  * to get summary text
  * to get 5 most important news
* /help - displays help
