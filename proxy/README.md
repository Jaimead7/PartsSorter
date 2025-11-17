# Parts sorter system: Reverse Proxy  


## Contact  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description  
Reverse proxy for the complete app.  


## Installation  
### Copy the config file.  
Copy the [nginx.conf](./nginx.conf) file into the nginx folder.  
The nginx folder is configured during docker compose volumes creation.  
The path is readed from the [.env](../.env.example).  
The default value is `/mnt/shared/nginx`.  

### Create docker container  
Running docker compose with the current [compose.yaml](../compose.yaml) will create the api and web containers.  
```bash
cd <parts sorter path>
docker compose up nginx
```
For creating the container alone (change the device paths).  
```bash
cd <parts sorter path>
docker run -d \
  --name nginx \
  --restart unless-stopped \
  -p 80:80 \
  --mount type=bind,source=/mnt/shared/nginx/nginx.conf,target=/etc/nginx/nginx.conf \
  --mount type=bind,source=/mnt/shared/nginx/conf.d/,target=/etc/nginx/conf.d/ \
  --mount type=bind,source=/mnt/shared/logs/nginx/,target=/var/log/nginx/ \
  --mount type=bind,source=/mnt/shared/nginx/ssl/,target=/etc/nginx/ssl/ \
  nginx:alpine
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