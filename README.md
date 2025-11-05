# Parts sorter system  


## Contact:  
> **Jaime Ávarez Díaz**  
> *e-mail:* alvarez.diaz.jaime1@gmail.com  


## Description:  
The objective of the project is to create a system for sorting parts from a conveyor.  
Parts on a conveyor are inspected by a camera and removed from the conveyor based on part type.  
The system consists on three parts:  
- A [**Capture App**](./capture/README.md) that takes the photos and send them to the server.  
- A [**API**](./api/README.md) that manages the database, process input images and notify the clients.  
- A [**Web App**](./web/README.md) to provide an interface for the final users.  

## Part list:  
- [Raspberry Pi 5 8GB](https://www.amazon.es/Raspberry-8GB-PCIe-M-2-NVMe/dp/B0CRMQCYXH/ref=sr_1_13?crid=2VI7Y35ZNZCTN&dib=eyJ2IjoiMSJ9.gx04gFjzZ9-r_ol_3WCSYithu1eedi8cYzCRgA2Ff_YPKzTl2T_p0FAJ_qEuLxCnnSxUivDXoAvtrMAgWuUTUOAjDubmGYDmQ8eHwqOHTaOQrXAEvt9ttMwrcx3jgZ4CFIQLkQ9ukGCEsMlbf8w0mB1IJnNcBDwtNXAQKLTGt2i8hcehyKDeWFP9tq6L1SBS_bA910hdljrgWlWoiEi22KBZC9s7-v50RV8CTgfn9GohIbo1Z7s-kpX81Jwwrklgtns4cr_THxo96FVAQXDSPjGmeZstHdApkW6Uy6EvKkc.wKOtfsL0zYzMNznIUTxfJAYNn014asH29wd4dKa6-yA&dib_tag=se&keywords=nvme%2Braspberry%2Bpi%2B5&qid=1752643231&sprefix=nvme%2Bras%2Caps%2C128&sr=8-13&th=1)  
- PCIe SSD M.2 NVMe shield for Raspberry Pi 5 (Kit with the Raspberry)  
- Raspberry Pi 5 metal box (Kit with the Raspberry)  
- 5V USB-C 27W Power Supply (Kit with the Raspberry)  
- Raspberry Pi 5 cooler fan (Kit with the Raspberry)  
- HDMI 4k cable (Kit with the Raspberry)  
- 64GB SD card for development (Kit with the Raspberry)  
- ~~[1TB M.2 NVMe SSD ~3W Kingston NV3](https://www.amazon.es/Kingston-Interno-500GB-2280-SNV3S-500G/dp/B0DBR3DZWG/ref=sr_1_4?__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3VV1NI3HOT2U9&dib=eyJ2IjoiMSJ9.bcp5dTrK-1Cfw42U1wr_uGgYTNtZlUgDNRJ_yPvcxdHU1E7dp5TUGGeBjB4UtX7bC9SL9tbNoLGwKtoZaIL9GIu-1w6SG_E50vTK0Qg9C4mNfY6WE4D1aEMPPOfRrO1PBoRXeLG6AI_HeExO7igWF0c4WgE-VmqoRBBlSoAjSb8lcJGnFH5X5o5L7e2vuUNnfNfZ_PWvQgbD7jmW5FyABH9YNKs81pUJk_ls9MbLpEhXzTvYZNP0-WYMYW8_230reVXRN0l2oMkW8LCy1IIxcIjB_afW5Ya6E4RmQVxtw_s.eBpFmT-TW4ih4YKS5Bp2WUYuIvYRZvn6C0fHzVXtOTY&dib_tag=se&keywords=kingston%2BNV2&qid=1752648292&sprefix=kingston%2Bnv2%2Caps%2C128&sr=8-4&th=1)~~ &rarr; This SSD has controller incompatibility with the RaspberryPi ([Read this article](https://wiki.geekworm.com/NVMe_SSD_boot_with_the_Raspberry_Pi_5)). Use a compatible SSD.  
- [Logitech C920 HD Pro Webcam](https://www.amazon.es/Logitech-C920-HD-Pro-C%C3%A1mara/dp/B006A2Q81M/ref=sr_1_7?__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=J7H1WUKNBP8K&dib=eyJ2IjoiMSJ9.dTYmmOK4oIgMZmQTrrB3URb7N_-kikuVBDHilwdhSEtNJgcPAF2BPhMTwS3v1JENcu_e1H4YEVGuwGrfAgzPOb6dRylCkVCc7xO0O8BpmJzAwa7zWPluO6x0e5t4ZtAn8KwmgKFbeSPevfvzmkyJZvNEj1xAjBLCw7Y1JyozSrduEFHwVx--QFohmI3YMAk0paPOdB_k8x-vp85Qr7RCxPrb_Q-k6xM7Cofg_2svuTkm2zGZd32AIfkkeQtfTQJ1zz7D2VZUP-oKHkoh4BYaCarq-2imef1ppkVdMEQMSpA.CWx8tcMN2m4TtvU5EauZjk0ZF1JMYf-ZRD59K6UKssw&dib_tag=se&keywords=logitech+webcam&qid=1752654840&sprefix=logitech+webcam%2Caps%2C112&sr=8-7)  
- [Logitech C270 Webcam](https://www.amazon.es/Logitech-Video-Llamadas-Correcci%C3%B3n-Iluminaci%C3%B3n-Chromebook/dp/B01BGBJ8Y0/ref=sr_1_4?crid=3F25ONUSVEM8V&dib=eyJ2IjoiMSJ9.dTYmmOK4oIgMZmQTrrB3URb7N_-kikuVBDHilwdhSEtNJgcPAF2BPhMTwS3v1JENcu_e1H4YEVGuwGrfAgzPOb6dRylCkVCc7xO0O8BpmJzAwa7zWPluO6x0e5t4ZtAn8KwmgKFbeSPevfvzmkyJZvNEj1xAjBLCw7Y1JyozSrduEFHwVx--QFohmI3YMAk0paPOdB_k8x-vp85Qr7RCxPrb_Q-k6xM7Cofg_2svuTkm2zGZd32AIfkkeQtfTQJ1zz7D2VZUP-oKHkoh4BYaCTrzPHIsO69WXvJE8PiGoKM.9s5yNkg1On8cFi-mV9rn3MuTUdgpHmpsC9JbeDGb-hY&dib_tag=se&keywords=logitech+webcam&qid=1752657719&sprefix=logitech+we%2Caps%2C137&sr=8-4)  
- [Relé 5V-In](https://www.amazon.es/Gebildet-Protecci%C3%B3n-Aislamiento-Optoacoplador-Compatible/dp/B0DPMNQ2MN/ref=sr_1_4?__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3NDJZ0MHA1KTK&dib=eyJ2IjoiMSJ9.Hflc2x-J27AvVQ--EM0tsT0t0v5-d-f-i75D_sNfrelYEqdSkAwjdFF726vsOsmtY1X3YDIOs3iO5f8JgcNeFmR4vTGat8nxqUe9gTbXdRog9NE8oLYM5wZijPMqRbXJxYMXcSE9PTNv48YCyQwRHxPI66AhZsmEtqafzlBkkaxAz2XPijxn2a3h8vAgx0JQ4YdeUQkyKrYIz8SGi0Ok-ybb1NxArYDP0KlZunAZX96fYQgascgEs8o9ECRBqsZLuECU91OxeHolcjzbvO-9EI6fepf1nXp2IHgXw6tY650.0FzyQuEt77CgiXR7VYEvFj_wyFF5fefz986xfYNituQ&dib_tag=se&keywords=rele%2B24v%2Braspberry%2Bpi&qid=1752658364&sprefix=rele%2B24v%2Braspberrypi%2Caps%2C104&sr=8-4&th=1)  

## Installation  

## License  
- **Capture App** &rarr; [AGPL-3.0](./capture/LICENSE)  
- **API** &rarr; [AGPL-3.0](./api/LICENSE)  
- **Web App** &rarr; [MIT](./web/LICENSE)  