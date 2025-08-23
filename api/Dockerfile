# 
FROM python:3.9

# 
WORKDIR /code
# entrypoint.shをコンテナ内にコピー
COPY ./api/entrypoint.sh /code/entrypoint.sh
# 
COPY ./api/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./api/app /code/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
