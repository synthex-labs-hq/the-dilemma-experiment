"""Entrypoint for running the simulation API server."""

from the_dilemma_experiment.api.app import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("the_dilemma_experiment.api.app:app", host="0.0.0.0", port=8000, reload=True)
