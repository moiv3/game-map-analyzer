async function fetchTaskQueueDb(){
    const signinStatusToken = window.localStorage.getItem('token');
    const result = await fetch("./api/video/task_status_db/", {
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
        renderTable(wipData, 'data-db-wip-table', ["任務編號", "遊戲類型","影片備註", "狀態", "上傳時間", "最後更新時間"]);
        const compData = resultJson["tasks_completed"];
        console.log(compData);
        renderTable(compData, 'data-db-comp-table', ["任務編號", "遊戲類型", "影片備註", "狀態", "最後更新時間", "地圖", "影片", "路徑分析", "系統訊息"]);
}

// Function to render table
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
            if ((header === "地圖" || header === "影片" || header === "路徑分析") && item[header]){
               const span = document.createElement('span');
               span.textContent = "Link";
               const anchor = document.createElement('a');
               anchor.href=item[header];
               anchor.setAttribute("target", "_blank");
               anchor.appendChild(span);
               const td = document.createElement('td');
               td.appendChild(anchor);
               tr.appendChild(td);
            }
            else{
                const td = document.createElement('td');
                td.textContent = item[header];
                if (header === '狀態' && item[header] === 'UPLOADED') {
                    td.textContent = item[header];
                    const button = document.createElement('button');
                    button.textContent = '點此開始分析';
                    button.onclick = () => processVideo(item, button);
    
                    td.appendChild(button);
                }    
                tr.appendChild(td);
            }

        });
        tbody.appendChild(tr);
    });
}

async function processVideo(item, button) {
    const signinStatusToken = window.localStorage.getItem('token');
    const uploadStatusMessage = document.querySelector("#video-process-status-message");

    if (!signinStatusToken){
        uploadStatusMessage.textContent = "登入狀態異常，請重新整理頁面"
        return false;
    }
    if (!confirm("即將開始分析，請確認是否送出分析需求？")){
        return false;
    }

    button.disabled = true;
    button.textContent = '已送出需求，請稍候';

    // check API key
    const task_id = item.任務編號;
    console.log(`Processing task with ID: ${task_id}`);
    // fetch and update 結果
    result = await fetch("./api/video/process_uploaded_video",{
        method:"POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${signinStatusToken}`
        },
        body: JSON.stringify({
            "task_id": task_id
        })
    });
    const resultJson = await result.json();
    console.log(resultJson);

    if (resultJson.ok){
        uploadStatusMessage.textContent = "成功送出需求，請到會員中心確認結果";
        button.textContent = '需求送出成功！';

    }
    else{
        console.log(resultJson.message);
        uploadStatusMessage.textContent = `送出需求失敗：${resultJson.message}`;
        button.textContent = '需求送出失敗';
    }
}


fetchTaskQueueDb();
checkTokenOnPageLoad();