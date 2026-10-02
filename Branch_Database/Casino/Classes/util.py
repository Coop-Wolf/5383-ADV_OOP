import re


# Letter first, then letters/digits/underscores, with at most one space
# in the middle (the space must be followed by at least one more character).
USERNAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?: [A-Za-z0-9_]+)?")
USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 10
RESERVED_NAMES = {"dealer", "house", "casino", "admin", "guest", "player", "players"}
 


class Util():
        
    @staticmethod
    def validate_username(raw):
        """Check a username typed by the player.
    
        Returns (clean_username, None) if it is valid, or (None, error_message)
        if it is not. Leading and trailing whitespace is removed first.
        """
        name = raw.strip()
    
        if not USERNAME_MIN_LENGTH <= len(name) <= USERNAME_MAX_LENGTH:
            return None, (
                f"Username must be {USERNAME_MIN_LENGTH} to {USERNAME_MAX_LENGTH} characters."
            )
        if not USERNAME_PATTERN.fullmatch(name):
            return None, (
                "Use letters, numbers, and underscores only, start with a letter, "
                "and use at most one space in the middle."
            )
        if name.lower() in RESERVED_NAMES:
            return None, "That name is reserved. Please choose another."
    
        return name, None