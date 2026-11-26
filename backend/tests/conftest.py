import os

# Settings needs this to import; create_engine does not connect until used.
os.environ.setdefault("DATABASE_URL", "postgresql://stonk:stonk@localhost:5432/stonk")
