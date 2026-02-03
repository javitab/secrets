###
### Delinea (SSApp) Secrets Retrieval Module
### Developed by John Avitable 02 February 2026
### Below module requires environment variables:
###     SSAPP_USERNAME
###     SSAPP_PASSWORD
###     SSAPP_BASEURL
###
### And also requires the following libraries:
###     httpx
###     pydantic
###     python-dotenv
###
### Usage Example:
###     ```python
###     from delinea import SSCreds
###
###    cred = SSCreds(
###        secret_id=1234,
###        slug_ident="username", # Optional, this shows default
###        slug_secret="password", # Optional, this shows default
###        )
###    print(f"id: {cred.secret_id} ident: {cred.ident} secret: {cred.secret}")
###    ```
###


import os
import typing
import httpx
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from functools import cached_property
from dotenv import load_dotenv

load_dotenv()


SSAPP_USERNAME = os.getenv("SSAPP_USERNAME")
SSAPP_PASSWORD = os.getenv("SSAPP_PASSWORD")

SSAPP_BASEURL = os.getenv("SSAPP_BASEURL")

SEC_NAME_AS_IDENT = [
    6041,  # IAM - Service Account
    6047,  # IAM - High Risk Service Account
]

current_access_token: str | None = None
current_refresh_token: str | None = None


class SSCreds(BaseModel):
    """
    Requires: secret_id (int)

    Accepts:
        slug_ident: str field slug for val_id default: username
        slug_secret: str field slug for val_sec default: password
    """

    secret_id: int
    slug_ident: str = "username"
    slug_secret: str = "password"
    cache_access_token: str = "delinea:access_token"
    cache_refresh_token: str = "delinea:refresh_token"
    cache_refresh_ctr: str = "delinea:refresh_ctr"
    _s: httpx.Client | None = None
    init_uuid: str = Field(default_factory=lambda x: str(uuid4()))
    token_type: typing.Literal["cached", "server", "refreshed"] = "cached"
    _sec_template: int = 0
    _sec_name: str | None = None
    _nolog: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow arbitrary types in the model
    )

    @cached_property
    def ident(self) -> str:
        """Returns value of credential username/identity"""

        ### Evaluate conditions to return self.sec_name
        if any(
            (
                self.slug_ident == "$self._sec_name",
                self._sec_template in SEC_NAME_AS_IDENT,
            )
        ):
            self.slug_ident = "$self._sec_name"
            return self._sec_name  # pyright: ignore[reportReturnType]

        ### Return slug as specified
        return self._getSlug(self.slug_ident)

    @cached_property
    def secret(self) -> str:
        """Returns value of secret"""
        return self._getSlug(self.slug_secret)

    @property
    def otp(self) -> str:
        return self._getTOTP()[0]["code"]  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues, reportOptionalSubscript]

    class Retrieval(typing.TypedDict):
        time: str
        slug: str
        call_stack: list[str]
        outcome: str
        error: str

    class ResponseOutDict(typing.TypedDict):
        request_url: str
        request_body: str | dict
        response_code: int
        request_headers: dict
        response_headers: dict

    def model_post_init(self, *args, **kwargs):
        print(f"Initializing Credential Request: {self.init_uuid}")

        self._s = httpx.Client()

        # Retrieve secret summary to get template and name
        sec_summ = self._getSecretSummary()
        self._sec_template = sec_summ["secretTemplateId"]
        self._sec_name = sec_summ["name"]

    class _Headers(typing.TypedDict):
        Authorization: str

    @property
    def _getHeaders(self) -> _Headers:
        headers: SSCreds._Headers = {"Authorization": "Bearer " + self._accessToken}
        return headers

    @property
    def _accessToken(self) -> str:
        """
        Uses three methods to retrieve an access_token:
        1. Retrieve access_token from cache, if exists
        2. Retrieve new access_token with refresh_token from cache, if exists
        3. Retrieve a new access_token from the server
        """
        if self._cachedAccessToken is not None:
            self.token_type = "cached"
            return self._cachedAccessToken
        return self._getServerAccessToken()  # pyright: ignore[reportReturnType]

    @property
    def _cachedAccessToken(self) -> typing.Union[str, None]:
        return current_access_token

    @property
    def _cachedRefreshToken(self) -> typing.Union[str, None]:
        return current_refresh_token

    def _getSlug(self, slug: str) -> str:
        try:
            resp = self.get(
                url="api/v1/secrets/{id}/fields/{slug}",
                params={"id": self.secret_id, "slug": slug},
            )
            resp.raise_for_status()
            return resp.text.strip('"')
        except Exception as e:
            raise e

    class OTPResponse(typing.TypedDict):
        code: str
        durationSeconds: int
        remainingSeconds: int

    def _getTOTP(self) -> OTPResponse | None | str:
        try:
            resp = self.get(
                url="api/v1/one-time-password-code/{id}",
                params={"id": self.secret_id},
            )
            resp.raise_for_status()
            return resp.text.strip('"')
        except Exception as e:
            raise e

    def _getSecretSummary(self) -> dict:
        resp = self.get(
            url="api/v1/secrets/{id}/summary", params={"id": self.secret_id}
        ).json()
        return resp

    class DelineaOAuth(BaseModel):
        access_token: str | None = None
        token_type: str | None = None
        expires_in: int | None = None
        refresh_token: str | None = None
        refresh_ctr: str | None = None

    def _getServerAccessToken(self) -> str:
        # Get new oauth token from server with creds
        cred = (SSAPP_USERNAME, SSAPP_PASSWORD)
        resp = self._s.post(  # pyright: ignore[reportOptionalMemberAccess]
            url=SSAPP_BASEURL + "oauth2/token",  # pyright: ignore[reportOptionalOperand]
            data={
                "grant_type": "password",
                "username": cred[0],
                "password": cred[1],
            },
        )
        del cred
        resp.raise_for_status()

        oauth = SSCreds.DelineaOAuth()
        resp = resp.json()
        oauth.access_token = resp["access_token"]
        oauth.token_type = resp["token_type"]
        oauth.expires_in = resp["expires_in"]
        oauth.refresh_token = resp["refresh_token"]

        # Save tokens to cache
        current_access_token = oauth.access_token
        current_refresh_token: str = oauth.refresh_token  # pyright: ignore[reportAssignmentType]

        return current_access_token  # pyright: ignore[reportReturnType]

    def post(
        self,
        url: str,
        data: dict = {},
        params: dict = {},
    ) -> httpx.Response:
        resp = self._s.post(  # pyright: ignore[reportOptionalMemberAccess]
            headers=self._getHeaders,  # pyright: ignore[reportArgumentType]
            url=SSAPP_BASEURL + url,  # pyright: ignore[reportOptionalOperand]
            params=params,
            data=data,
        )
        resp.raise_for_status()
        return resp

    def get(
        self,
        url: str,
        params: dict = {},
    ) -> httpx.Response:
        def sendRequest():
            if self._s is None:
                self._initSession()
            resp = self._s.get(  # pyright: ignore[reportOptionalMemberAccess]
                headers=self._getHeaders,
                url=SSAPP_BASEURL + url,  # pyright: ignore[reportOptionalOperand]
                params=params,
            )
            resp.raise_for_status()
            if "API_AccessDenied" in resp.text:
                raise RuntimeError("Unable to retrieve secret, access denied.")
            return resp

        resp = sendRequest()
        if "Authentication failed or expired token" in resp.text:
            print("Deleting token and repeating request")
            current_access_token = None
            current_refresh_token = None
            resp = sendRequest()
            resp.raise_for_status()


        return resp
