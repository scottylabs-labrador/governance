import os
from functools import lru_cache

from keycloak import KeycloakAdmin

from meta.logger import get_app_logger

# Expose the username so the word "admin" won't be filtered in GitHub Actions...
KEYCLOAK_USERNAME = "admin"


@lru_cache(maxsize=1)
def get_keycloak_client() -> KeycloakClient:
    return KeycloakClient()

class KeycloakClient:
    def __init__(self) -> None:
        self.logger = get_app_logger()

        server_url = os.getenv("KEYCLOAK_SERVER_URL")
        if not server_url:
            msg = "KEYCLOAK_SERVER_URL is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        password = os.getenv("KEYCLOAK_PASSWORD")
        if not password:
            msg = "KEYCLOAK_PASSWORD is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        realm_name = os.getenv("KEYCLOAK_REALM")
        if not realm_name:
            msg = "KEYCLOAK_REALM is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        client_id = os.getenv("KEYCLOAK_CLIENT_ID")
        if not client_id:
            msg = "KEYCLOAK_CLIENT_ID is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        user_realm_name = os.getenv("KEYCLOAK_USER_REALM")
        if not user_realm_name:
            msg = "KEYCLOAK_USER_REALM is not set"
            self.logger.critical(msg)
            raise RuntimeError(msg)

        self.keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=KEYCLOAK_USERNAME,
            password=password,
            realm_name=realm_name,
            client_id=client_id,
            user_realm_name=user_realm_name,
            verify=True,
        )


    def get_user_id_by_username(self, username: str) -> str | None:
        users = self.keycloak_admin.get_users(
            query={"username": username, "exact": True},
        )

        if not users:
            return None

        # Used `exact` = True, so we should only have one user.
        return users[0]["id"] # type: ignore
