from getpass import getpass

from app.core.database import SessionLocal
from app.models.reviewer import Reviewer
from app.services.auth import hash_password


def main():
    db = SessionLocal()

    try:
        username = input(
            "Reviewer username: "
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

        password_confirmation = getpass(
            "Confirm password: "
        )

        if password != password_confirmation:
            print("Passwords do not match.")
            return

        if len(password) < 12:
            print(
                "Password must contain at least 12 characters."
            )
            return

        reviewer = Reviewer(
            username=username,
            password_hash=hash_password(
                password
            ),
            role="reviewer",
            is_active=True,
        )

        db.add(reviewer)
        db.commit()
        db.refresh(reviewer)

        print(
            f"Reviewer created successfully: "
            f"id={reviewer.id}, "
            f"username={reviewer.username}, "
            f"role={reviewer.role}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
