from fastapi import FastAPI

app = FastAPI(
    title="ChildSafe",
    description="Digital child protection and online safety platform.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "ChildSafe API",
        "status": "online",
    }
