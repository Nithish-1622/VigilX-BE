"""
CatalystUserRepository — Reads and writes ALL user management data
to Zoho Catalyst Cloud SQL (Data Store / ZCQL), NOT Neon Postgres.

This is the single source of truth for:
  - User profiles (catalyst_uid, email, display name, avatar)
  - Roles (ADMIN, SUPERVISOR, INVESTIGATOR, ANALYST, POLICYMAKER, USER)
  - Auth provider (EMAIL, GOOGLE, ZOHO)

Table: UserProfile (in Catalyst Console → Data Store)
Columns:
  - ROWID               (bigint, system auto)
  - CREATORID           (bigint, system auto)
  - CREATEDTIME         (datetime, system auto)
  - MODIFIEDTIME        (datetime, system auto)
  - catalyst_uid        (text)
  - email               (text)
  - First_Name          (text)
  - Last_Name           (text)
  - display_Name        (text)
  - role                (text)
  - auth_provider       (text)
  - profile_image_url   (text)
  - is_active           (boolean)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _get_zcql(request=None):
    """
    Initialize the zcatalyst SDK and return the ZCQL service instance.
    In AppSail, Catalyst injects credentials automatically via the request.
    """
    try:
        import zcatalyst_sdk
        if request is not None:
            raw_request = getattr(request, "_request", request)
            app = zcatalyst_sdk.initialize(req=raw_request)
        else:
            # Server-to-server (no request context, e.g. management commands)
            app = zcatalyst_sdk.initialize()
        return app.zcql()
    except Exception as exc:
        logger.error("Failed to initialize Catalyst ZCQL service: %s", exc)
        raise


def _get_datastore(table_name: str, request=None):
    """Return a Catalyst Data Store table instance for direct row operations."""
    try:
        import zcatalyst_sdk
        if request is not None:
            raw_request = getattr(request, "_request", request)
            app = zcatalyst_sdk.initialize(req=raw_request)
        else:
            app = zcatalyst_sdk.initialize()
        return app.datastore().table(table_name)
    except Exception as exc:
        logger.error("Failed to initialize Catalyst Data Store: %s", exc)
        raise


TABLE = "UserProfile"

# Catalyst role name → VigilX role
CATALYST_ROLE_MAP = {
    "App Administrator": "ADMIN",
    "Admin": "ADMIN",
    "Supervisor": "SUPERVISOR",
    "Investigator": "INVESTIGATOR",
    "Crime Analyst": "ANALYST",
    "Analyst": "ANALYST",
    "Policymaker": "POLICYMAKER",
    "User": "USER",
}

CATALYST_PROVIDER_MAP = {
    "zoho": "ZOHO",
    "google": "GOOGLE",
    "email": "EMAIL",
    "EMAIL": "EMAIL",
}


class CatalystUserRepository:
    """
    Repository for User Management backed by Zoho Catalyst Cloud SQL.

    Matches exact table schema created in Catalyst Data Store.
    """

    @staticmethod
    def get_or_create_from_catalyst(
        catalyst_user: dict,
        request=None
    ) -> tuple[dict, bool]:
        """
        Upsert a user profile in Catalyst Cloud SQL from a Catalyst user dict.

        Returns (user_profile_dict, created) where created=True on first login.
        Handles cross-provider email linking: same email → same profile row.
        """
        email = (catalyst_user.get("email_id") or "").strip().lower()
        catalyst_uid = str(catalyst_user.get("user_id") or "").strip()
        first_name = catalyst_user.get("first_name", "")
        last_name = catalyst_user.get("last_name", "")
        display_name = f"{first_name} {last_name}".strip() or email
        profile_img = catalyst_user.get("profile_image_url", "")

        platform = str(catalyst_user.get("platform", "email")).lower()
        auth_provider = CATALYST_PROVIDER_MAP.get(platform, "EMAIL")

        role_details = catalyst_user.get("role_details") or {}
        role_name = role_details.get("role_name", "Investigator")
        role = CATALYST_ROLE_MAP.get(role_name, "INVESTIGATOR")

        if not email:
            raise ValueError("Catalyst user has no email — cannot sync to Catalyst Cloud SQL")

        try:
            # ── 1. Try fetch by catalyst_uid ──────────────────────────────────
            existing = CatalystUserRepository.get_by_catalyst_uid(catalyst_uid, request)

            # ── 2. Fall back to email lookup (cross-provider linking) ──────────
            if existing is None:
                existing = CatalystUserRepository.get_by_email(email, request)

            if existing is not None:
                # Extract row ID safely
                row_id = existing.get("ROWID") or existing.get("UserProfile", {}).get("ROWID")
                if row_id:
                    table = _get_datastore(TABLE, request)
                    table.update_row({
                        "ROWID": row_id,
                        "catalyst_uid": catalyst_uid,
                        "First_Name": first_name,
                        "Last_Name": last_name,
                        "display_Name": display_name,
                        "role": role,
                        "auth_provider": auth_provider,
                        "profile_image_url": profile_img,
                        "is_active": True,
                    })
                existing.update({
                    "catalyst_uid": catalyst_uid,
                    "First_Name": first_name,
                    "Last_Name": last_name,
                    "display_Name": display_name,
                    "role": role,
                    "auth_provider": auth_provider,
                    "profile_image_url": profile_img,
                    "is_active": True,
                })
                logger.debug("Catalyst Cloud SQL: existing user updated — %s", email)
                return existing, False

            # ── 3. Create new row (first login) ───────────────────────────────
            table = _get_datastore(TABLE, request)
            new_row = {
                "catalyst_uid": catalyst_uid,
                "email": email,
                "First_Name": first_name,
                "Last_Name": last_name,
                "display_Name": display_name,
                "role": role,
                "auth_provider": auth_provider,
                "profile_image_url": profile_img,
                "is_active": True,
            }
            result = table.insert_row(new_row)
            row_id = result.get("ROWID") or result.get("rowId") or result.get("UserProfile", {}).get("ROWID") or ""
            new_row["ROWID"] = row_id
            logger.info(
                "Catalyst Cloud SQL: new user created — %s (role=%s, provider=%s)",
                email, role, auth_provider
            )
            return new_row, True

        except Exception as exc:
            logger.exception("CatalystUserRepository error: %s", exc)
            raise

    @staticmethod
    def get_by_email(email: str, request=None) -> Optional[dict]:
        """Fetch a user profile by email from Catalyst Cloud SQL."""
        try:
            zcql = _get_zcql(request)
            safe_email = email.lower().replace("'", "''")
            rows = zcql.execute_query(
                f"SELECT * FROM {TABLE} WHERE email = '{safe_email}'"
            )
            if rows and len(rows) > 0:
                row_data = rows[0].get("UserProfile", rows[0])
                return row_data
            return None
        except Exception as exc:
            logger.error("get_by_email failed: %s", exc)
            return None

    @staticmethod
    def get_by_catalyst_uid(uid: str, request=None) -> Optional[dict]:
        """Fetch a user profile by Catalyst UID."""
        if not uid:
            return None
        try:
            zcql = _get_zcql(request)
            safe_uid = uid.replace("'", "''")
            rows = zcql.execute_query(
                f"SELECT * FROM {TABLE} WHERE catalyst_uid = '{safe_uid}'"
            )
            if rows and len(rows) > 0:
                row_data = rows[0].get("UserProfile", rows[0])
                return row_data
            return None
        except Exception as exc:
            logger.error("get_by_catalyst_uid failed: %s", exc)
            return None

    @staticmethod
    def update_last_login(catalyst_uid: str, request=None) -> None:
        """Catalyst automatically updates MODIFIEDTIME on row touch."""
        pass

    @staticmethod
    def update_role(catalyst_uid: str, new_role: str, request=None) -> None:
        """Update the role of a user in Catalyst Cloud SQL."""
        try:
            zcql = _get_zcql(request)
            safe_uid = catalyst_uid.replace("'", "''")
            safe_role = new_role.replace("'", "''")
            zcql.execute_query(
                f"UPDATE {TABLE} SET role = '{safe_role}' "
                f"WHERE catalyst_uid = '{safe_uid}'"
            )
        except Exception as exc:
            logger.error("update_role failed: %s", exc)

    @staticmethod
    def list_all(request=None) -> list[dict]:
        """List all user profiles from Catalyst Cloud SQL."""
        try:
            zcql = _get_zcql(request)
            rows = zcql.execute_query(f"SELECT * FROM {TABLE}")
            if not rows:
                return []
            return [r.get("UserProfile", r) for r in rows]
        except Exception as exc:
            logger.error("list_all failed: %s", exc)
            return []

    @staticmethod
    def build_profile_dict(row: dict) -> dict:
        """Convert a Catalyst Cloud SQL row into a standard profile response dict."""
        data = row.get("UserProfile", row)
        return {
            "id": str(data.get("ROWID", "")),
            "catalyst_uid": data.get("catalyst_uid", ""),
            "email": data.get("email", ""),
            "first_name": data.get("First_Name", ""),
            "last_name": data.get("Last_Name", ""),
            "display_name": data.get("display_Name", "") or f"{data.get('First_Name', '')} {data.get('Last_Name', '')}".strip() or data.get("email", ""),
            "role": data.get("role", "INVESTIGATOR"),
            "auth_provider": data.get("auth_provider", "EMAIL"),
            "profile_image_url": data.get("profile_image_url") or None,
            "is_active": data.get("is_active", True),
            "created_at": data.get("CREATEDTIME"),
            "modified_at": data.get("MODIFIEDTIME"),
        }

