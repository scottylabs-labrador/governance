"""Allow running as python -m governance_py from repo root with PYTHONPATH=__meta/validators."""

from .main import main

if __name__ == "__main__":
    main()
