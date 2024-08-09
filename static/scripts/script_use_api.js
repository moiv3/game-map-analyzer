let apiKeyGlobal;
const youtubeUrlSubmitBtn = document.querySelector("#youtube-url-submit");
youtubeUrlSubmitBtn.addEventListener("click", async function(event) {
    event.preventDefault();
    const youtubeUrlInput = document.querySelector("#youtube-url").value;
    console.log(youtubeUrlInput);
    const videoIdValid = await validVideoId(youtubeUrlInput);
    console.log(videoIdValid);
    if (videoIdValid){
        embedVideo(youtubeUrlInput);
                newBtn = document.createElement("button");
        newBtn.textContent="確認完成，送出解析需求";
        submitQueryDiv = document.querySelector("#submit-query");
        submitQueryDiv.appendChild(newBtn);
        newBtn.addEventListener("click", async function(event){
            if (!confirm("Are you sure to process this video?")){
                return;
            }
            else{
                const systemMessageBox = document.querySelector("#system-message");
                systemMessageBox.textContent = "Processing video, please wait...";

                // fake process for testing
                fetchResult = await fetch("./api/process_fake_video/",{
                    method:"POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "youtube_id": youtubeUrlInput,
                        "api_key": apiKeyGlobal
                    }),
                });
                // TODO: real process here
                // fetchResult = await fetch("./api/process-video/");

                fetchResultJson = await fetchResult.json();
                console.log(fetchResultJson);
                if (fetchResultJson.ok){
                    systemMessageBox.textContent = fetchResultJson.file;
                    const parseMessageBox = document.querySelector("#parsing-result");
                    parseMessageBox.style.display = "block";
                    parseMessageBox.textContent = "Parse complete, result below:";
                    parseImg = document.querySelector("#parsed-image");
                    parseImg.src = "../static/images/output.jpg";
                    }
                else if (fetchResultJson.error){
                    const parseMessageBox = document.querySelector("#parsing-result");
                    parseMessageBox.style.display = "block";
                    parseMessageBox.textContent = `Error: ${fetchResultJson.message}`;
                }

            }
        });
    }

});

const fetchApiKeyButton = document.querySelector("#fetch-api-key-button");
fetchApiKeyButton.addEventListener("click", checkApiKey);

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

function validVideoId(id) {
    return new Promise((resolve, reject) => {
        var img = new Image();
        img.src = "http://img.youtube.com/vi/" + id + "/mqdefault.jpg";
        img.onload = function () {
            const isValid = checkThumbnail(this.width);
            console.log(isValid);
            resolve(isValid);
        }
        img.onerror = function () {
            reject(new Error("Image failed to load"));
        }
    });
}

async function checkThumbnail(width) {
    //HACK a mq thumbnail has width of 320.
    //if the video does not exist(therefore thumbnail don't exist), a default thumbnail of 120 width is returned.
    if (width === 120) {
        const systemMessageBox = document.querySelector("#system-message");
        systemMessageBox.textContent = "Video doesn't exist, try again";
        return false;
    }
    else{
        const systemMessageBox = document.querySelector("#system-message");
        systemMessageBox.textContent = "Video confirmed, loading video...";
        return true;
    }
}

function addYoutubePlayer(){
    // 2. This code loads the IFrame Player API code asynchronously.
    var tag = document.createElement('script');

    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // 3. This function creates an <iframe> (and YouTube player)
    //    after the API code downloads.
    var player;
    function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: 'M7lc1UVf-VE',
        playerVars: {
            'playsinline': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
        });
    }

    // 4. The API will call this function when the video player is ready.
    function onPlayerReady(event) {
        event.target.playVideo();
    }

    // 5. The API calls this function when the player's state changes.
    //    The function indicates that when playing a video (state=1),
    //    the player should play for six seconds and then stop.
    var done = false;
    function onPlayerStateChange(event) {
        if (event.data == YT.PlayerState.PLAYING && !done) {
        setTimeout(stopVideo, 6000);
        done = true;
        }
    }
    function stopVideo() {
        player.stopVideo();
    }
}

function embedVideo(id) {
    const playerDiv = document.getElementById("player");
    playerDiv.innerHTML = `<iframe width="560" height="315" src="https://www.youtube.com/embed/${id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
}

async function generateCorrectSigninElements(){
    console.log("generateCorrectSigninElements");
    const tokenStatus = await checkToken();
    if (tokenStatus){
        apiWebDiv = document.querySelector("#api-web-signed-in");
        apiWebDiv.style.display = "block";
    }

}
generateCorrectSigninElements();