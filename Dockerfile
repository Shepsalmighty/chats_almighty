FROM python:alpine
#RUN apk update && apk add python3 && apk add py3-dotenv
COPY twitch_bot /app/twitch_bot
WORKDIR /app
COPY requirements.txt .
RUN apk add --update py-pip
RUN pip install -r requirements.txt
CMD ["python", "-m", "twitch_bot"]
#array above was an array of strings, probably need another command eg
# ["python3", "__main__.py"]

