async function renderName() {
    userData = await checkToken();
    if (userData){
        memberGreetingDiv = document.querySelector("#member-greeting");
        memberGreetingDiv.textContent = userData.name + " 您好！"
    }
}

renderName();