# Setup  

## Folder structure  
```
/
|--- ...
|--- etc
|    |--- udev
|    |    |--- rules.d
|    |    |    |--- 99-webcam.rules
|    |    |    `--- ...
|    |    `--- ...
|    `--- ...
|--- home
|    |--- dev
|    |    |--- Projects
|    |    `--- ...
|    |--- production
|    |    `--- .config
|    |         `--- autostart
|    |              `--- open-image-stream.desktop
|    `--- ...
|--- ...
|--- mnt
|    |--- shared
|    |    |--- datasets
|    |    |--- images
|    |    |    |--- production
|    |    |    `--- ...
|    |    |--- label-studio
|    |    |--- logs
|    |    |    |--- nginx
|    |    |    `--- ...
|    |    |--- models
|    |    |--- nginx
|    |    |    |--- conf.d
|    |    |    |--- ssl
|    |    |    |--- nginx.conf
|    |    |    `--- ...
|    |    |--- postgres
|    |    `--- ...
|    `--- ...
`--- ...
```
```bash
su dev

mkdir ~/Projects

sudo mkdir -p /etc/udev/rules.d

sudo mkdir /mnt/shared
sudo chmod 777 /mnt/shared
sudo setfacl -R -d -m u::rwx,g::rwx,o::rwx /mnt/shared

sudo mkdir /mnt/shared/datasets
sudo mkdir -p /mnt/shared/images/production
sudo mkdir /mnt/shared/label-studio
sudo mkdir -p /mnt/shared/logs/nginx
sudo mkdir /mnt/shared/models
sudo mkdir -p /mnt/shared/nginx/conf.d
sudo mkdir /mnt/shared/nginx/ssl
sudo mkdir /mnt/shared/postgres
```
## Download project  
```bash
su dev
cd ~/Projects
git clone https://github.com/Jaimead7/PartsSorter.git
```

## Copy config files  
```bash
su dev
cd ~/Projects/PartsSorter

cp ./proxy/nginx.conf /mnt/shared/nginx/
chmod 644 /mnt/shared/nginx/nginx.conf

sudo cp ./scripts/99-webcam.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

sudo -u production mkdir -p /home/production/.config/autostart
sudo cp ./scripts/open-image-stream.desktop /home/production/.config/autostart/
sudo chown production:production /home/production/.config/autostart/open-image-stream.desktop
sudo chmod 644 /home/production/.config/autostart/open-image-stream.desktop
```

## Create .env files  
```bash
su dev
cd ~/Projects/PartsSorter

cp ./.env.example ./.env  # Change env vars
cp ./api/.env.example ./api/.env.docker  # Change env vars
cp ./capture/.env.example ./capture/.env.docker  # Change env vars
cp ./label-studio/.env.example ./label-studio/.env.docker  # Change env vars
cp ./postgres/.env.example ./postgres/.env.docker  # Change env vars
cp ./web/.env.example ./web/.env.docker  # Change env vars
```

## Run project
```bash
su dev
cd ~/Projects/PartsSorter

sudo docker compose up -d
```