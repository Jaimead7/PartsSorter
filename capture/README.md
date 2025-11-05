# Parts sorter system: Camera App  


## Contact  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description  
Program for capturing images and manage actuator signals.  


## Installation  
### Create a .env.docker.  
Use the [.env.example](./.env.example) as example.  
- ORIGIN_NAME &rarr; Name for the device. This name should be on the database for manage the origin of the images uploaded.  
- API_IP &rarr; Base IP of the API.  
- LOGGING_LVL &rarr; Logging level.  
- LOGS_PATH &rarr; Path where the logs will be saved.  
- ACTUATOR_PIN &rarr; Output pin connected to the relay of the actuator.  
- CAMERA_SENSOR_PIN &rarr; Input pin of the sensor that detects the part in the camera position.  
- ACTUATOR_SENSOR_PIN &rarr; Input pin of the sensor that detects the part in the actuator position.  
- SENSORS_DISTANCE &rarr; Distance between sensors in mm.  
- TAPE_SPEED &rarr; Speed of the tape of the conveyor in mm/s.  


### Create docker container  
Running docker compose with the current [compose.yaml](../compose.yaml) will create the api container.  
```bash
cd <parts sorter path>
docker compose up capture
```
For creating the container alone (change the device paths).  
```bash
cd <parts sorter path>
docker build -t parts-sorter-capture -f ./capture/Dockerfile ./capture
docker run -d \
  --name capture \
  --restart unless-stopped \
  --env-file ./capture/.env.docker \
  --device /dev/gpiochip4:/dev/gpiochip4 \
  --device /dev/video0:/dev/video0 \
  --mount type=bind,source=/mnt/shared/logs,target=/app/dist/logs \
  parts-sorter-capture
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