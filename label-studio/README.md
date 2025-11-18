# Parts sorter system: Label studio  


## Contact  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description  
Label studio sql auxiliar scripts.  


## Installation  
### Create a .env.docker.  
Use the [.env.example](./.env.example) as example.  
- LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED &rarr; Enable local storage.  
- LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT &rarr; Local storage path.  

### Create docker container  
Running docker compose with the current [compose.yaml](../compose.yaml).  
```bash
cd <parts sorter path>
docker compose up label-studio
```
For creating the container alone (change the device paths).  
```bash
cd <parts sorter path>
docker run -d \
  --name label-studio \
  --init \
  --restart unless-stopped \
  -p 8000:8000 \
  --mount type=bind,source=/mnt/shared/label-studio,target=/label-studio/data \
  --mount type=bind,source=/mnt/shared/images,target=/local-storage/images \
  heartexlabs/label-studio:latest
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