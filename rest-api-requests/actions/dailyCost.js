const Minio = require('minio');

// Fixed cost per kWh
const COST_PER_KWH = 0.125;

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
        console.log(`Fetching objects for date: ${date}`);
        // Assume device folders like 'kitchen/', 'tv/', etc.
        const devices = ['kitchen', 'tv', 'livingroom']; // This could also be fetched dynamically if needed
        let totalCost = 0.0;
        let deviceCosts = {};

        for (let device of devices) {
            const fileName = `${device}/${date}.json`;
            console.log(`Processing file: ${fileName}`);

            try {
                const data = await minioClient.getObject(bucketName, fileName);
                const body = await streamToString(data);
                const jsonData = JSON.parse(body);
                const cost = jsonData.consumption * COST_PER_KWH;
                
                deviceCosts[device] = cost;
                totalCost += cost;
            } catch (err) {
                console.log(`Failed to process file for ${device} on ${date}: ${err}`);
                // Continue processing other devices even if one fails
            }
        }

        console.log(`Total cost for all devices: $${totalCost.toFixed(2)}`);

        return {
            message: "Cost calculation complete",
            date: date,
            total_cost: `$${totalCost.toFixed(2)}`,
            detailed_costs: deviceCosts
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
