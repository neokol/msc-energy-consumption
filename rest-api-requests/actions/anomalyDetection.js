const Minio = require('minio');

// Threshold for consumption anomaly detection
const ANOMALY_THRESHOLD = 500;

async function main(params) {
    const minioClient = new Minio.Client({
        endPoint: '20.19.91.100',
        port: 9100,
        useSSL: false,
        accessKey: 'admin',
        secretKey: 'admin123'
    });

    const bucketName = 'home-energy-logs';
    const date = params.date;  // Expecting date in YYYY-MM-DD format

    if (!date) {
        return { error: "Missing 'date' parameter" };
    }

    try {
        console.log(`Checking for anomalies in consumption on ${date}`);
        let anomalies = [];

        // List all device directories dynamically
        const deviceStream = minioClient.listObjects(bucketName, '', true, '/');

        for await (const device of deviceStream) {
            const deviceName = device.prefix.split('/')[0]; // Get the device name by splitting the prefix
            const fileName = `${device.prefix}${date}.json`;
            console.log(`Processing file: ${fileName}`);

            try {
                const data = await minioClient.getObject(bucketName, fileName);
                const body = await streamToString(data);
                const jsonData = JSON.parse(body);
                
                if (jsonData.consumption > ANOMALY_THRESHOLD) {
                    console.log(`Anomaly detected: ${deviceName} consumed ${jsonData.consumption} kWh`);
                    anomalies.push({device: deviceName, consumption: jsonData.consumption, date: date});
                }
            } catch (err) {
                console.log(`Failed to process file for ${deviceName} on ${date}: ${err}`);
            }
        }

        if (anomalies.length === 0) {
            return { message: "No anomalies found for " + date };
        }

        return {
            message: "Anomaly detection complete",
            date: date,
            anomalies: anomalies
        };
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
