    **OPENWHISK**

- How to install:

```sh
git clone https://github.com/apache/openwhisk.git
cd openwhisk
sudo apt install openjdk-8-jdk
sudo apt install nodejs
sudo apt install npm
```

- How to build:

Run to build Openwhisk

```sh
./gradlew :core:standalone:build
```

```sh
sudo java -Dwhisk.standalone.host.name=0.0.0.0 -Dwhisk.standalone.host.internal=127.0.0.1 -Dwhisk.standalone.host.external=0.0.0.0 -jar ./bin/openwhisk-standalone.jar --couchdb --kafka --api-gw --kafka-ui
```

How to create a action:

1. Create a package.json file like

```javascript
   {
   "name": "minio-action",
   "main": "index.js",
   "dependencies": {
   "minio": "^7.0.18"
   }
   }
```

2. Create a index.js file with the function openwhisk need to run

3. Install module dependencies using NPM.

   ```sh
   npm install
   ```

4. Create a .zip archive containing all files (including all dependencies)

```sh
   zip -r action.zip *
```

5. Create the action from the zip file.

```sh
   wsk action create packageAction --kind nodejs:20 action.zip --web true
```

    **MINIO - RABBITMQ - NODERED**

```sh
mkdir minio
Transfer docker-compose.yml
cd minio
docker compose up -d
```

    **FASTAPI**

How to run

Activate Virtual Enviroment

```sh
.\.venv\Scripts\activate
```

```sh
uvicorn main:app --reload
```
