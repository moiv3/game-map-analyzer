async function renderMember() {
    userData = await checkToken();
    if (userData){
        const memberNameDiv = document.querySelector("#member-name");
        memberNameDiv.textContent = userData.name;
        const memberEmailDiv = document.querySelector("#member-email");
        memberEmailDiv.textContent = userData.email;
    }
}

async function getMemberPreferences(){
    const signinStatusToken = window.localStorage.getItem('token');
    const memberPreferences = await fetch("/api/preferences",{
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${signinStatusToken}`
        }
    });
    const memberPreferencesJson = await memberPreferences.json();
    
    console.log("Obtained user preference data.");

    if (memberPreferencesJson.ok){
        if (memberPreferencesJson.member_preferences.send_mail == 1){
            document.querySelector("#send-mail-true").checked = true;
            sendMailGlobal = true;
        }
        else{
            document.querySelector("#send-mail-false").checked = true;
            sendMailGlobal = false;
        }
    }
}

async function editMemberPreferences(){
    const sendMailChecked = document.querySelector('input[name="send_mail"]:checked').value;
    const preferenceResultText = document.querySelector("#preferences-result-text");
    let sendMailValue;

    if ((sendMailChecked === "Yes" && sendMailGlobal === true) || (sendMailChecked === "No" && sendMailGlobal === false)){
        preferenceResultText.textContent = "設定相同，未變更。"
        editMemberPreferencesBtn.disabled = false;
        setTimeout(() => preferenceResultText.textContent = "", 3000);
        return false;
    }
    else {
        console.log("送出變更中，請稍候...");
    }

    if (sendMailChecked === "Yes"){
        sendMailValue = true;
    }
    else{
        sendMailValue = false;
    }

    let sendMailRequest = {};
    sendMailRequest["send_mail"] = sendMailValue;

    const signinStatusToken = window.localStorage.getItem('token');
    const memberPreferences = await fetch("/api/preferences",{
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${signinStatusToken}`
        },
        body: JSON.stringify(sendMailRequest)
    });
    const memberPreferencesJson = await memberPreferences.json();
    
    console.log("Obtained response from server.");

    if (memberPreferencesJson.ok){
        preferenceResultText.textContent = "變更成功！即將重新整理頁面。";
        setTimeout(() => window.location.reload(), 3000);
        editMemberPreferencesBtn.disabled = false;
    }
    else if (memberPreferencesJson.error){
        preferenceResultText.textContent = `變更失敗。錯誤訊息：${memberPreferencesJson.message}。`;
        setTimeout(() => preferenceResultText.textContent = "", 3000);
        editMemberPreferencesBtn.disabled = false;
        return false;
    }
}


let sendMailGlobal;
checkTokenOnPageLoad();
renderMember();
getMemberPreferences();
const editMemberPreferencesBtn = document.querySelector("#edit-preferences");
editMemberPreferencesBtn.addEventListener("click", async (params) => {
    event.preventDefault();
    editMemberPreferencesBtn.disabled = true;
    await editMemberPreferences();
})