"""FastAPI application for the IntelliNotify Environment."""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv-core is required.") from e

try:
    from ..models import IntelliNotifyAction, IntelliNotifyObservation
    from .intellinotify_env_environment import IntelliNotifyEnvironment
except (ModuleNotFoundError, ImportError):
    from models import IntelliNotifyAction, IntelliNotifyObservation
    from server.intellinotify_env_environment import IntelliNotifyEnvironment

app = create_app(
    IntelliNotifyEnvironment,
    IntelliNotifyAction,
    IntelliNotifyObservation,
    env_name="intellinotify_env",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    main(port=args.port)

# Required by openenv validator
if __name__ == "__main__":
    main()
