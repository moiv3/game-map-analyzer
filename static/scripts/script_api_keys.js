const getCurrentKeyButton = document.querySelector("#current-key");
getCurrentKeyButton.addEventListener("click", async function(event){
    const signinStatusToken = window.localStorage.getItem('token');
    // maybe...add actual auth here?
    if (!signinStatusToken){
        console.log("No token!")
        // edit TEXT on the webpage
        const systemStatus = document.querySelector("#system-status");
        systemStatus.textContent = "Not signed in, please refresh page, thx"
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
        console.log(currentKeyJson);
        const currentKeyResultText = document.querySelector("#current-key-result");
        currentKeyResultText.textContent = currentKeyJson.api_keys;

    }
})

const getNewKeyButton = document.querySelector("#get-new-key");
getNewKeyButton.addEventListener("click", async function(event){
    const signinStatusToken = window.localStorage.getItem('token');
    // maybe...add actual auth here?
    if (!signinStatusToken){
        console.log("No token!")
        // edit TEXT on the webpage
        const systemStatus = document.querySelector("#system-status");
        systemStatus.textContent = "Not signed in, please refresh page, thx"
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
        const newKeyResultText = document.querySelector("#get-new-key-result");
        newKeyResultText.textContent = newKeyJson.api_key;

    }
})