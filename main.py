# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Marcelo Munhoz

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
