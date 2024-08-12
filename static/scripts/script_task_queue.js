// async function fetchTaskQueueRedis(){
//     const result = await fetch("./task-status/", {
//         method:"GET"
//     });
//     const resultJson = await result.json();
//     console.log(resultJson);
//     console.log(resultJson["active"]["celery@Huang-SP"]);
//     if (resultJson["active"]["celery@Huang-SP"].length > 0){
//         const data = resultJson["active"]["celery@Huang-SP"];
//         renderTable(data, 'data-redis-table', ["id", "time_start"]);
//     }
//     else{
//         console.log("No task queue data found!");
//     }
// }

async function fetchTaskQueueRedis() {
    try {
        const result = await fetch("./task-status/", {
            method: "GET"
        });
        const resultJson = await result.json();
        console.log(resultJson);

        const allTasks = [];

        if (resultJson["active"]) {
            // Iterate over each worker in the 'active' tasks
            for (const workerName in resultJson["active"]) {
                if (resultJson["active"].hasOwnProperty(workerName)) {
                    const tasks = resultJson["active"][workerName];
                    
                    tasks.forEach(task => {
                        task.worker = workerName;  // Add worker name to each task object
                    });

                    allTasks.push(...tasks);  // Combine all tasks into one list
                }
            }

            if (allTasks.length > 0) {
                renderTable(allTasks, 'data-redis-table', ["worker", "id", "time_start"]);
            } else {
                console.log("No task queue data found!");
            }
        } else {
            console.log("No active tasks found!");
        }
    } catch (error) {
        console.error("Error fetching task queue:", error);
    }
}

async function fetchTaskQueueDb(){
    const result = await fetch("./task-status-db/", {
        method:"GET"
    });
    const resultJson = await result.json();
    console.log(resultJson);

    if (resultJson["tasks_wip"].length > 0){
        const data = resultJson["tasks_wip"];
        renderTable(data, 'data-db-wip-table', ["task_id", "api_key", "youtube_id", "status", "date_updated"]);
    }
    else{
        console.log("No task queue data found! (DB, WIP)");
    }

    if (resultJson["tasks_completed"].length > 0){
        const data = resultJson["tasks_completed"];
        renderTable(data, 'data-db-comp-table', ["task_id", "api_key", "youtube_id", "status", "date_updated"]);
    }
    else{
        console.log("No task queue data found! (DB, COMP)");
    }
}

fetchTaskQueueRedis();
fetchTaskQueueDb();

// const data = [
//     { name: 'John', age: 30, city: 'New York' },
//     { name: 'Anna', age: 22, city: 'London' },
//     { name: 'Mike', age: 32, city: 'Chicago' }
// ];

// Function to render the table
// data: array of objects
// headers: array of strings
function renderTable(data, tableId, headers) {
    const table = document.getElementById(tableId);
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

    // Clear existing table data
    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Get keys (headers) from the first object
    // const headers = Object.keys(data[0]);

    // Brian: if headers defined:
    // const headers = ["id", "time_start"]

    // Create table headers
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.charAt(0).toUpperCase() + header.slice(1);
        thead.appendChild(th);
    });

    // Create table rows
    data.forEach(item => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = item[header];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

// function renderTable(data) {
//     const table = document.getElementById('data-table');
//     const thead = table.querySelector('thead tr');
//     const tbody = table.querySelector('tbody');

//     // Clear existing table data
//     thead.innerHTML = '';
//     tbody.innerHTML = '';

//     // Get keys (headers) from the first object
//     // const headers = Object.keys(data[0]);

//     // Brian: if headers defined:
//     const headers = ["id", "time_start"]

//     // Create table headers
//     headers.forEach(header => {
//         const th = document.createElement('th');
//         th.textContent = header.charAt(0).toUpperCase() + header.slice(1);
//         thead.appendChild(th);
//     });

//     // Create table rows
//     data.forEach(item => {
//         const tr = document.createElement('tr');
//         headers.forEach(header => {
//             const td = document.createElement('td');
//             td.textContent = item[header];
//             tr.appendChild(td);
//         });
//         tbody.appendChild(tr);
//     });
// }


// Render the table with the data
// renderTable(data);