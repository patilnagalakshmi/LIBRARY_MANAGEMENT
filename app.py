from fastapi import FastAPI,Request
from routing import router
from pyinstrument import Profiler
from security import SecurityHeadersMiddleware
app = FastAPI()

app.include_router(router)
app.add_middleware(SecurityHeadersMiddleware)
@app.middleware("http")
async def memory_profiling_middleware(request: Request, call_next):
    # Start the profiler
    profiler = Profiler()
    profiler.start()
 
    # Process the request
    response = await call_next(request)
 
    # Stop the profiler after the response is generated
    profiler.stop()
 
    # Save profiler results into a human-readable HTML file
    endpoint = request.url.path.replace('/', '_')
    with open(f"memory_profile_{endpoint}.html", "w") as f:
        f.write(profiler.output_html())
 
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

