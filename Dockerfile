FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Copy the .env file to the container
COPY .env ./.env

# Load environment variables from .env file using ENV
ENV $(cat .env | grep -v ^# | xargs)

# this following is using the flask
#CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# the following is using fastapi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]


#CMD ["chmod", "+x", "script.sh"]

#CMD ["./script.sh", "run-app"]
