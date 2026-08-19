from getpass import getpass

from app.core.database import SessionLocal
from app.models.reviewer import Reviewer
from app.services.auth import hash_password


def main():
    db = SessionLocal()

    try:
        username = input(
            "Admin username: "
        ).strip()

        if not username:
            print("Username cannot be empty.")
            return

        existing = (
            db.query(Reviewer)
            .filter(
                Reviewer.username == username
            )
            .first()
        )

        if existing is not None:
            print(
                "A reviewer with this username already exists."
            )
            return

        password = getpass(
            "Password: "
        )

        confirmation = getpass(
            "Confirm password: "
        )

        if password != confirmation:
            print("Passwords do not match.")
            return

        if len(password) < 12:
            print(
                "Password must contain at least 12 characters."
            )
            return

        admin = Reviewer(
            username=username,
            password_hash=hash_password(
                password
            ),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            "Admin created successfully: "
            f"id={admin.id}, "
            f"username={admin.username}, "
            f"role={admin.role}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
