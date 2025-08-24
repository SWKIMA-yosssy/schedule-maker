# 
FROM python:3.9

# 
WORKDIR /code
# entrypoint.shをコンテナ内にコピー
COPY ./entrypoint.sh ./entrypoint.sh
# 
COPY ./requirements.txt ./requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY . .

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
