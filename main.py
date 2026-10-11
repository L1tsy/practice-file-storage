from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers_file
import routers_user

app = FastAPI(
    title="File Storage Backend",
    version="1.0.0",
    description="Сервис управления метаданными файлов и папок",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers_user.router)
app.include_router(routers_file.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)