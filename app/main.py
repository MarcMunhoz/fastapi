# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Marcelo Munhoz

from fastapi import FastAPI  # type: ignore

app = FastAPI()


@app.get('/')
def read_root():
  return {'message': 'Hello, World!'}


@app.get('/health')
def health_check():
  return {'status': 'ok'}
