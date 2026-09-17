"""One-off helper: logs into Life360 as you and prints every Circle member's
name + id, so you can match them up to the `life360_member_id` field in
backend/seed.py (or update existing User rows directly).

Run with: python -m worker.list_life360_members
"""

from life360 import Life360

from . import config


def main():
    client = Life360(username=config.LIFE360_USERNAME, password=config.LIFE360_PASSWORD)
    client.authenticate()

    circles = client.get_circles()
    circle = next((c for c in circles if c["name"] == config.LIFE360_CIRCLE_NAME), None)
    if circle is None:
        names = [c["name"] for c in circles]
        raise RuntimeError(f"Circle '{config.LIFE360_CIRCLE_NAME}' not found. Available: {names}")

    members = client.get_circle_members(circle["id"])
    print(f"Circle: {circle['name']}\n")
    for member in members:
        first = member.get("firstName", "")
        last = member.get("lastName", "")
        print(f"  {first} {last}: {member['id']}")


if __name__ == "__main__":
    main()
