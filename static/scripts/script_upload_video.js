
function addUploadButtonListener(){
    document.getElementById('upload-form').addEventListener('submit', async function(event){
        event.preventDefault();

        if (!confirm("Are you sure to upload this video?")){
            return false;
        }

        const signinStatusToken = window.localStorage.getItem('token');
        if (!signinStatusToken){
            console.log("No token detected!");
            return false;
        }

        const fileInput = document.querySelector('#file-id');
        console.log(fileInput);
        console.log(fileInput.files[0]);
        const file = fileInput.files[0];

        if (!file){
            document.querySelector('#upload-status-message').textContent = 'Error: No file selected.';
            return;
        }

        const fileSizeMb = (file.size / 1024 / 1024).toFixed(2);
        const fileName = file.name;
        const re = /\.mp4$/i;

        console.log("File size:" + fileSizeMb + "MB");

        if (!re.exec(fileName)) {
            document.querySelector('#upload-status-message').textContent = '錯誤：不支援此檔案格式，請再試一次。';
        }
        else if (fileSizeMb > 15) {        
            document.querySelector('#upload-status-message').textContent = '錯誤：檔案大小超出上限(' + fileSizeMb + 'MB)，請再試一次。';
            return;
        }
        else {        
            document.querySelector('#upload-status-message').textContent = '請稍候，檔案上傳中...';

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('./api/upload/', {
                    method: 'POST',
                    body: formData,
                    headers: {Authorization: `Bearer ${signinStatusToken}`}
                });

                const result = await response.json();
                if (response.ok) {
                    document.querySelector('#upload-response-message').textContent = `File uploaded successfully: ${result.filename}`;
                }
                else {
                    document.querySelector('#upload-response-message').textContent = `Error: ${result.detail}`;
                }
            }
            catch (error) {
                document.querySelector('#upload-response-message').textContent = `Error: ${error.message}`;
            }
            return;
        }
    });
}

async function fetchUploadedVideos(){
    const signinStatusToken = window.localStorage.getItem('token');
    if (!signinStatusToken){
        console.log("No token detected!");
        return false;
    }
    const result = await fetch("./api/get_uploaded_videos/", {
        method:"GET",
        headers: {Authorization: `Bearer ${signinStatusToken}`}
    });

    const resultJson = await result.json();
    console.log(resultJson);

    if (resultJson["uploaded_videos"].length > 0){
        const data = resultJson["uploaded_videos"];
        renderTable(data, 'uploaded-videos-table', ["user_id", "video_id", "status", "error_message", "create_time"]);
    }
    else{
        console.log("No uploaded video data found!");
    }

}

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

            // Check if the status is 'NOT PROCESSED' and add a button
            if (header === 'status' && item[header] === 'NOT PROCESSED') {
                td.textContent = item[header];
                const button = document.createElement('button');
                button.textContent = '點此開始分析';
                button.onclick = () => processVideo(item, button);

                td.appendChild(button);
            } else {
                td.textContent = item[header];
            }

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

async function checkApiKey() {
    console.log("Entering function checkApiKey");
    const signinStatusToken = window.localStorage.getItem('token');
    if (!signinStatusToken){
        const resultText = document.querySelector("#api-key-result-text");
        resultText.textContent = "Not signed in, please sign in again!";
        return false;
    }
    else{
        const apiKey = await fetch("./api/get_current_key",{
            method: "get",
            headers: {Authorization: `Bearer ${signinStatusToken}`}
        });
        const apiKeyJson = await apiKey.json();
        console.log(apiKeyJson.api_keys);

        if (apiKeyJson.user_id && apiKeyJson.api_keys){
            const resultText = document.querySelector("#api-key-result-text");
            resultText.textContent = apiKeyJson.api_keys;
            apiKeyGlobal = apiKeyJson.api_keys[0];
            return apiKeyJson.api_keys[0];
        }
        else if (apiKeyJson.user_id){
            const resultText = document.querySelector("#api-key-result-text");
            resultText.textContent = "尚未取得有效的API key, 請至會員中心生成";
            return false;
        }
        else{
            const resultText = document.querySelector("#api-key-result-text");
            resultText.textContent = `Error: ${apiKeyJson.message}`;
            return false;
        }
    }
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
    if (!apiKeyGlobal){
        console.log("test");
        uploadStatusMessage.textContent = "無API key, 請點選上面按鈕讀取，或至會員中心申請API key";
        return false;
    }

    button.disabled = true;
    button.textContent = '已送出需求，請稍候';

    // check API key
    console.log(`Processing video with ID: ${item.video_id}`);
    console.log(`API key: ${apiKeyGlobal}`);
    // fetch and update 結果
    result = await fetch("./api/process_uploaded_video",{
        method:"POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${signinStatusToken}`
        },
        body: JSON.stringify({
            "video_id": item.video_id,
            "api_key": apiKeyGlobal
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
        uploadStatusMessage.textContent = "送出需求失敗，請聯繫管理員確認";
        button.textContent = '需求送出失敗';
    }
}

addUploadButtonListener();
fetchUploadedVideos();
let apiKeyGlobal;
const fetchApiKeyButton = document.querySelector("#fetch-api-key-button");
fetchApiKeyButton.addEventListener("click", checkApiKey);
