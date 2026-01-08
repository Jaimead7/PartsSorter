#  Parts sorter system API


## Contact:  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description  
API for managing the database and process the images.  


## Installation  
### Create a .env.docker.  
Use the [.env.example](./.env.example) as example.  
- LOGS_PATH &rarr; Path where the logs will be saved.  
- LOGGING_LVL &rarr; Logging level.  
- SERVER_IP &rarr; IP where the API will be exposed.  
- SERVER_PORT &rarr; Port where the API will be exposed.  
- DATABASE_URL &rarr; URL of the database with the protocol used.  
- HOST_IP &rarr; IP of the host of the container. Used for sending the URL of the files shared.  


### Create docker container  
Running docker compose with the current [compose.yaml](../compose.yaml) will create the postgres container.  
```bash
cd <parts sorter path>
docker compose up api
```
For creating the container alone (change the device paths).  
```bash
cd <parts sorter path>
docker build -t parts-sorter-api -f ./api/Dockerfile ./api
docker run -d \
  --name api \
  --restart unless-stopped \
  --env-file ./api/.env.docker \
  -p 8000:8000 \
  --mount type=bind,source=/mnt/shared/images,target=/api/dist/images \
  --mount type=bind,source=/mnt/shared/models,target=/api/dist/models \
  --mount type=bind,source=/mnt/shared/datasets,target=/api/dist/datasets \
  --mount type=bind,source=/mnt/shared/logs,target=/api/dist/logs \
  parts-sorter-api
```

## License  
This component is licensed under the **[MIT License](./LICENSE)**.  
### Permissions  
- ✅ Commercial use  
- ✅ Modification  
- ✅ Distribution  
- ✅ Private use  
- ✅ Sublicensing  

### Requirements  
- ℹ️ Include copyright notice  
- ℹ️ Include license copy  

### Limitations  
- ❌ No liability  
- ❌ No warranty  

### Third-Party Attributions  
This software includes third-party components under various licenses.  
See **[ATTRIBUTIONS.md](./ATTRIBUTIONS.md)** for complete details.  

### Project Context  
This component is part of a larger project with multiple licenses.  
Other components may have different license terms.  