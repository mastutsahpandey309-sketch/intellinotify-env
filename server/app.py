"""server/app.py — required by openenv validator."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # re-export root app


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
