
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
    const signinStatusToken = window.localStorage.getItem('token');
    const result = await fetch("./task-status-db/", {
        method:"GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${signinStatusToken}`
        },
    });
    const resultJson = await result.json();
    console.log(resultJson);

        const wipData = resultJson["tasks_wip"];
        console.log(wipData);
        renderTable(wipData, 'data-db-wip-table', ["task_id", "source", "video_id", "status", "date_updated"]);
        const compData = resultJson["tasks_completed"];
        console.log(compData);
        renderTable(compData, 'data-db-comp-table', ["task_id", "source", "video_id", "status", "date_updated", "image", "video", "json", "message"]);
    // if (resultJson["tasks_wip"].length > 0){
    //     }
    // else{
    //     console.log("No task queue data found! (DB, WIP)");
    // }

    // if (resultJson["tasks_completed"].length > 0){
    //     const compData = resultJson["tasks_completed"];
    //     console.log(compData);
    //     renderTable(compData, 'data-db-comp-table', ["task_id", "source", "video_id", "status", "date_updated", "image", "video", "json", "message"]);
    // }
    // else{
    //     console.log("No task queue data found! (DB, COMP)");
    // }
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

    // Check if the data array is empty
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="' + headers.length + '">無符合條件的任務。</td></tr>';
        return;
    }
    // Get keys (headers) from the first object
    // const headers = Object.keys(data[0]);

    // Brian: if headers defined:
    // const headers = ["id", "time_start"]

    // Create table headers
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        thead.appendChild(th);
    });

    // Create table rows
    data.forEach(item => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            if (header === "image" || header === "video" || header === "json"){
               const span = document.createElement('span')
               span.textContent = "Link";
               const anchor = document.createElement('a');
               anchor.href=item[header];
               anchor.appendChild(span);
               const td = document.createElement('td');
               td.appendChild(anchor);
               tr.appendChild(td);
            }
            else{
                const td = document.createElement('td');
                td.textContent = item[header];
                tr.appendChild(td);
            }

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