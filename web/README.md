# Parts sorter system: Web App  


## Contact  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description  
User interface of the parts sorter system as a web app.  


## Installation  
### Create a .env.docker.  
Use the [.env.example](./.env.example) as example.  
- LOGS_PATH &rarr; Path where the logs will be saved.  
- LOGGING_LVL &rarr; Logging level.  
SERVER_IP &rarr; IP where the server will be exposed.  
SERVER_PORT &rarr; Port where the server will be exposed.  
- API_URL &rarr; Base IP of the API.  

### Create docker container  
Running docker compose with the current [compose.yaml](../compose.yaml) will create the api container.  
```bash
cd <parts sorter path>
docker compose up web
```
For creating the container alone (change the device paths).  
```bash
cd <parts sorter path>
docker build -t parts-sorter-web -f ./web/Dockerfile ./web
docker run -d \
  --name web \
  --restart unless-stopped \
  --env-file ./web/.env.docker \
  -p 5000:5000 \
  --mount type=bind,source=/mnt/shared/logs,target=/app/dist/logs \
  parts-sorter-web
```

## License  
[MIT](./LICENSE)  