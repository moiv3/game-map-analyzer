
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
        renderTable(data, 'uploaded-videos-table', ["user_id", "video_id", "video_url", "create_time"]);
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


addUploadButtonListener();
fetchUploadedVideos();