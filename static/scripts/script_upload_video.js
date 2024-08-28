// note: upload_video page also loads script_task_queue.js

function addUploadButtonListener(){
    document.getElementById('upload-form').addEventListener('submit', async function(event){
        event.preventDefault();

        if (!confirm("確認上傳這部影片？")){
            return false;
        }

        const signinStatusToken = window.localStorage.getItem('token');
        if (!signinStatusToken){
            alert("登入狀態異常，請重新整理後再試一次");
            console.log("No token detected!");
            return false;
        }

        const fileInput = document.querySelector('#file-id');
        console.log(fileInput);
        console.log(fileInput.files[0]);
        const file = fileInput.files[0];

        if (!file){
            document.querySelector('#upload-status-message').textContent = '錯誤：請選擇上傳影片';
            return;
        }

        const fileSizeMb = (file.size / 1024 / 1024).toFixed(2);
        const fileName = file.name;
        const re = /\.mp4$/i;

        console.log("File size:" + fileSizeMb + "MB");

        if (!re.exec(fileName)) {
            document.querySelector('#upload-status-message').textContent = '錯誤：不支援此檔案格式，請再試一次。';
        }
        else if (fileSizeMb > 5) {        
            document.querySelector('#upload-status-message').textContent = '錯誤：檔案大小超出上限(' + fileSizeMb + 'MB)，請再試一次。';
            return;
        }
        else {        
            document.querySelector('#upload-status-message').textContent = '請稍候，檔案上傳中...';

            submitVideoButton = document.querySelector("#submit-video-button");
            submitVideoButton.disabled = true;

            const gameType = document.querySelector("#game-type").value;
            console.log(gameType);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('gameType', gameType);

            try {
                const response = await fetch('./api/video/upload_video', {
                    method: 'POST',
                    body: formData,
                    headers: {Authorization: `Bearer ${signinStatusToken}`}
                });

                const result = await response.json();
                console.log(result);
                if (result.error) {
                    document.querySelector('#upload-response-message').textContent = `錯誤：${result.message}`;
                    }
                else if (result.ok) {
                    document.querySelector('#upload-response-message').textContent = `成功上傳影片！系統訊息：${result.message}。請稍候，即將重新整理畫面...`;
                    setTimeout(() => window.location.reload(), 5000);
                }
                else {
                    document.querySelector('#upload-response-message').textContent = `錯誤：${result.detail}`;
                }
            }
            catch (error) {
                document.querySelector('#upload-response-message').textContent = `錯誤：${error.message}`;
            }
            submitVideoButton.disabled = false;
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
    const result = await fetch("./task-status-db/", {
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

    button.disabled = true;
    button.textContent = '已送出需求，請稍候';

    // check API key
    console.log(`Processing video with ID: ${item.video_id}`);
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
        uploadStatusMessage.textContent = `送出需求失敗：${resultJson.message}`;
        button.textContent = '需求送出失敗';
    }
}

addUploadButtonListener();
checkTokenOnPageLoad();
