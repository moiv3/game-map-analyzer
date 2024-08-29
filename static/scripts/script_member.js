async function renderName() {
    const userData = await checkToken();
    if (userData){
        memberGreetingDiv = document.querySelector("#member-greeting");
        memberGreetingDiv.textContent = userData.name + " 您好！"
    }
    else{
        alert("尚未登入，請先登入會員！")
        window.location.replace("./");
    }
}

renderName();