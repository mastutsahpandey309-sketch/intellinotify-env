from openenv.core.env_server.http_server import create_app
from .models import IntelliNotifyAction, IntelliNotifyObservation
from .environment import IntelliNotifyEnvironment

app = create_app(
    IntelliNotifyEnvironment,
    IntelliNotifyAction,
    IntelliNotifyObservation,
    env_name="intellinotify",
    max_concurrent_envs=1,
)

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
