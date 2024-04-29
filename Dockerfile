FROM python
RUN apt update && apt upgrade
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "query_nr.py"]