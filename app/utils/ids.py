import uuid


def generate_unique_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())
