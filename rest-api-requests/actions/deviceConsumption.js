const Minio = require('minio');

async function main(params) {
    const minioClient = new Minio.Client({
        endPoint: '20.19.91.100',
        port: 9100,
        useSSL: false,
        accessKey: 'admin',
        secretKey: 'admin123'
    });

    const bucketName = 'home-energy-logs';
    const deviceId = params.device_id;

    if (!deviceId) {
        return { error: "Missing 'device_id' parameter" };
    }

    try {
        console.log(`Fetching objects for device_id: ${deviceId}`);
        const stream = minioClient.listObjects(bucketName, deviceId, true);
        let totalConsumption = 0.0;
        let objectCount = 0;

        for await (const obj of stream) {
            console.log(`Processing object: ${obj.name}`);
            const data = await minioClient.getObject(bucketName, obj.name);
            const body = await streamToString(data);
            const jsonData = JSON.parse(body);
            totalConsumption += jsonData.consumption;
            objectCount++;
        }

        console.log(`Total objects processed: ${objectCount}`);
        console.log(`Total consumption: ${totalConsumption}`);

        return { message: "Data processed", device_id: deviceId, total_consumption: totalConsumption };
    } catch (err) {
        console.error("Error:", err.message);
        return { error: err.message };
    }
}

function streamToString(stream) {
    const chunks = [];
    return new Promise((resolve, reject) => {
        stream.on('data', chunk => chunks.push(chunk));
        stream.on('error', reject);
        stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf-8')));
    });
}

exports.main = main;
