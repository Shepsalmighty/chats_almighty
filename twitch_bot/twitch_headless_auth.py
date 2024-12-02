import asyncio
import os
from pathlib import Path
from os import getenv
from dotenv import load_dotenv
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, TwitchAPIException
from flask import Flask, redirect, request
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
APP_ID = getenv("TWITCH_CLIENT_ID")
APP_SECRET = getenv("TWITCH_CLIENT_SECRET")
TARGET_SCOPE = [AuthScope.CHAT_EDIT, AuthScope.CHAT_READ]
MY_URL = 'http://localhost:5000/login/confirm'


app = Flask(__name__)
twitch: Twitch
auth: UserAuthenticator


@app.route('/login')
def login():
    return redirect(auth.return_auth_url())


@app.route('/login/confirm')
async def login_confirm():
    state = request.args.get('state')
    if state != auth.state:
        return 'Bad state', 401
    code = request.args.get('code')
    if code is None:
        return 'Missing code', 400
    try:
        # TODO use UserAuthenticationStorageHelper (twitch.chat.view line 145) instead of authenticate
        # TODO provide the UserAuthenticationStorageHelper with a custom auth_generator_func
        #TODO that is similar to UserAuthenticationStorageHelper._default_auth_gen but uses "code"
        token, refresh = await auth.authenticate(user_token=code)
        await twitch.set_user_authentication(token, TARGET_SCOPE, refresh)
    except TwitchAPIException as e:
        return 'Failed to generate auth token', 400
    return 'Successfully authenticated!'


async def twitch_setup():
    global twitch, auth
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, TARGET_SCOPE, url=MY_URL)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as ex:
        ex.submit(app.run)
        ex.submit(asyncio.run, twitch_setup())

# asyncio.run(twitch_setup())