FROM python:alpine
#RUN apk update && apk add python3 && apk add py3-dotenv
COPY twitch_bot /app/twitch_bot
WORKDIR /app
COPY requirements.txt .
#RUN apk add --update py-pip
RUN pip install -r requirements.txt
#CMD ["python", "sqlite_db.py"]
#TODO replace ENTRYPOINT with a script called entrypoint.sh for example that checks if our database
#TODO exists (db/twitch_bot.db), if not creates it, then RUN ["python", "-m", "twitch_bot"]
#TODO ... OR just create the db file in python first, then run the ENTRYPOINT cmd
ENTRYPOINT ["python", "-m", "twitch_bot"]
#array above was an array of strings, probably need another command eg
# ["python3", "__main__.py"]

