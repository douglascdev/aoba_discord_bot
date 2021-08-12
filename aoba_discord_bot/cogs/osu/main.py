import requests

from discord.ext import commands
from datetime import datetime, timedelta

from discord.ext.commands import Context


class Osu(commands.Cog, name="Osu"):
    API_BASE_URL = "https://osu.ppy.sh/api/v2/"
    API_OAUTH_URL = "https://osu.ppy.sh/oauth/token"

    def __init__(self):
        """
        The osu! API requires the client id and a secret to request a token. Create a credentials.txt file in the same
        folder as this file and paste the id in the first line and the secret in the second. Access your account
        settings(https://osu.ppy.sh/home/account/edit#oauth) to get the id and secret.
        """
        with open(
            "C:\\Users\\Douglas\\PycharmProjects\\aoba_discord_bot\\aoba_discord_bot\\cogs\\osu\\credentials.txt",
            "r",
        ) as credentials_file:
            self.client_id, self.client_secret = credentials_file.read().splitlines()
        self._access_token_info = None
        self._token_expires_dt = None

    def _get_authorization_header(self) -> dict:
        """
        Handles the request for OAuth token and re-requesting it when expired.
        return: dictionary with the authorization header with a valid OAuth token
        """
        now = datetime.now()

        def token_expired() -> bool:
            return self._token_expires_dt is not None and now >= self._token_expires_dt

        if self._access_token_info is None or token_expired():
            self._access_token_info = self._client_credentials_grant()
            secs_to_expire = int(self._access_token_info.get("expires_in"))
            self._token_expires_dt = now + timedelta(seconds=secs_to_expire)

        access_token = self._access_token_info.get("access_token")

        return {"Authorization": f"Bearer {access_token}"}

    def _client_credentials_grant(self) -> dict:
        """
        Sends a post request for a new client credential token.
        return: Dictionary with token_type(str=Bearer), expires_in(int in seconds), access_token(str)
        """
        body = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }
        return requests.post(url=Osu.API_OAUTH_URL, data=body).json()

    @commands.command()
    async def get_score_pp(self, ctx: Context, beatmap_id: int, user_id: int):
        url = f"{self.API_BASE_URL}beatmaps/{beatmap_id}/scores/users/{user_id}"
        body = {
            "mode": "std",
            # "mods": "",
        }
        response = requests.get(
            url=url, data=body, headers=self._get_authorization_header()
        ).json()
        pp = response.get("score").get("pp")
        await ctx.send(content=f"Player has a {round(pp)}pp score on this map!")
