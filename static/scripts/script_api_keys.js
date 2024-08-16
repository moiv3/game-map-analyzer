const getCurrentKeyButton = document.querySelector("#current-key");
getCurrentKeyButton.addEventListener("click", async function(event){
    const signinStatusToken = window.localStorage.getItem('token');
    const systemStatus = document.querySelector("#system-status");
    if (!signinStatusToken){
        console.log("No token!");
        systemStatus.textContent = "登入驗證異常，請重新整理後，再試一次";
        return false;
    }
    else{
        const currentKey = await fetch("./api/get_current_key",{
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${signinStatusToken}`
            }
        });
        const currentKeyJson = await currentKey.json();
        const newKeyResultText = document.querySelector("#get-new-key-result");
        const currentKeyResultText = document.querySelector("#current-key-result");
        if(currentKeyJson.ok){
            newKeyResultText.textContent = "";
            currentKeyResultText.textContent = `API key：${currentKeyJson.api_keys}`;
        }
        else{
            newKeyResultText.textContent = "";
            currentKeyResultText.textContent = "";
            systemStatus.textContent = "取得API key資訊時發生異常，請重新整理後，再試一次";
        }
    }
})

const getNewKeyButton = document.querySelector("#get-new-key");
getNewKeyButton.addEventListener("click", async function(event){
    const signinStatusToken = window.localStorage.getItem('token');
    if (!signinStatusToken){
        console.log("No token!");
        const systemStatus = document.querySelector("#system-status");
        systemStatus.textContent = "登入驗證異常，請重新整理後，再試一次";
        return false;
    }
    else{
        const newKey = await fetch("./api/generate_new_key",{
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${signinStatusToken}`
            }
        });
        const newKeyJson = await newKey.json();
        console.log(newKeyJson);
        if(newKeyJson.ok){
            const newKeyResultText = document.querySelector("#get-new-key-result");
            newKeyResultText.textContent = `申請/更新成功，您的API key：${newKeyJson.api_key}`;
            const currentKeyResultText = document.querySelector("#current-key-result");
            currentKeyResultText.textContent = `API key：${newKeyJson.api_key}`;
        }
        else{
            newKeyResultText.textContent = "";
            currentKeyResultText.textContent = "";
            systemStatus.textContent = "申請/更新API key時發生異常，請重新整理後，再試一次";
        }


    }
})