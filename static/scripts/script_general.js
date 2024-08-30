// check if there is a token in localStorage. if yes, fetch auth API to verify that token.
// The auth API will perform and respond with the data or error message.
async function checkToken(){
    let signinStatusToken = window.localStorage.getItem('token');
    if (!signinStatusToken){
        return false;
    }
    else{
        const signinResponse = await fetch("/api/user/auth",{
            method: "get",
            headers: {Authorization: `Bearer ${signinStatusToken}`}
        });
        const signinResponseJson = await signinResponse.json();
        if (!signinResponseJson.data){
        return false;
        }
        else{
            return signinResponseJson.data;
        }
    }
}

async function checkTokenOnPageLoad(){
    const userData = await checkToken();
    if (!userData){
        alert("尚未登入，請先登入會員！")
        window.location.replace("./");
    }
}

// signout function
async function removeSigninToken(){
    localStorage.removeItem("token");
    alert("您已成功登出，即將為您導向至首頁！");
    window.location.href = "/";
}

// creates HTML elements of curtain and signin form
function createCurtainAndSigninForm(){    
    let curtainElement = document.createElement("div");
    curtainElement.classList = "curtain active";

    let signupSquareElement = document.createElement("div");
    signupSquareElement.classList="signup-form-bg";
    curtainElement.appendChild(signupSquareElement);

    // let signupDecorationBarElement = document.createElement("div");
    // signupDecorationBarElement.classList="decoration-bar";
    // signupSquareElement.appendChild(signupDecorationBarElement);

    let buttonElement = document.createElement("button");
    buttonElement.classList="deactivate-curtain-button";
    buttonElement.addEventListener("click", (event) => {
        deactivateCurtain();
    });
    signupSquareElement.appendChild(buttonElement);

    let signupTitleElement = document.createElement("div");
    signupTitleElement.classList="header-3 bold signin gray-70";
    signupTitleElement.textContent="會員登入";
    signupSquareElement.appendChild(signupTitleElement);

    let formElement = document.createElement("form");
    formElement.classList = "signin-form";
    formElement.id = "signin_form";
    formElement.method = "post";
    signupSquareElement.appendChild(formElement);

    let inputUsernameElement = document.createElement("input");
    inputUsernameElement.classList = "body";
    inputUsernameElement.type = "text";
    inputUsernameElement.name = "username_name"
    inputUsernameElement.id = "username_id";
    inputUsernameElement.placeholder = "請輸入email";
    formElement.appendChild(inputUsernameElement);

    let inputPasswordElement = document.createElement("input");
    inputPasswordElement.classList = "body";
    inputPasswordElement.type = "password";
    inputPasswordElement.name = "password_name"
    inputPasswordElement.id = "password_id";
    inputPasswordElement.placeholder = "請輸入密碼";
    formElement.appendChild(inputPasswordElement);

    let signinButtonElement = document.createElement("button");
    signinButtonElement.classList = "btn";
    signinButtonElement.id = "signin_button";
    signinButtonElement.textContent="登入";
    formElement.appendChild(signinButtonElement);

    let signinResponseElement = document.createElement("div");
    signinResponseElement.classList="signin-response-text";
    signinResponseElement.display="none";
    formElement.appendChild(signinResponseElement);

    let signupContainerElement = document.createElement("div");
    signupContainerElement.classList = "signup-container gray-70";
    formElement.appendChild(signupContainerElement);

    let signupPromptElement = document.createElement("span");
    signupPromptElement.classList = "signup-text";
    signupPromptElement.textContent = "新使用者，請 ";
    signupContainerElement.appendChild(signupPromptElement);

    let signupAnchorElement = document.createElement("a");
    signupAnchorElement.textContent="點此免費註冊";
    signupAnchorElement.style.color="blue";
    signupAnchorElement.href="#";
    signupAnchorElement.onclick= () => toggleSignupPrompt();
    signupContainerElement.appendChild(signupAnchorElement);
    
    let bodyElement = document.querySelector("body");
    bodyElement.appendChild(curtainElement);
}

// curtain element (signin/signup form) activation and deactivation
function activateCurtain(event){
    let curtainElement = document.querySelector(".curtain");
    // curtain is already created => deactivate
    if (curtainElement){
        curtainElement.classList.add("active");
    }
    // curtain is not created => create curtain, then activate (add event listeners)
    else{
        createCurtainAndSigninForm();
        const signinForm = document.querySelector("#signin_form");
        signinForm.addEventListener("submit", handleSigninEvent);
    }
}

function deactivateCurtain(){
    let curtainElement = document.querySelector(".curtain");
    curtainElement.classList.remove("active");
}


// signin/signup form toggle when clicking on link.
let signupPromptFlag = false;
function toggleSignupPrompt(){
    if(!signupPromptFlag){
        // console.log("Hit toggle Signup Prompt! Signin -> Signup");

        const titleElement = document.querySelector(".signin");
        titleElement.textContent = "新會員註冊";

        const formElement = document.querySelector("#signin_form");        
        const usernameIdElement = document.querySelector("#username_id");

        const newNameInputElement = document.createElement("input");
        newNameInputElement.type="text";
        newNameInputElement.name="name_name";
        newNameInputElement.id="name_id";
        newNameInputElement.placeholder="請輸入姓名";
        newNameInputElement.classList="signup-input body";
        formElement.insertBefore(newNameInputElement, usernameIdElement);
        
        const signInButtonElement = document.querySelector("#signin_button");
        signInButtonElement.textContent = "註冊";

        const signinTextElement = document.querySelector(".signup-text");
        signinTextElement.textContent = "已註冊過之會員，請";

        const promptElement = document.querySelector(".signup-container a");
        promptElement.style.color="blue";
        promptElement.textContent = "點此登入";

        formElement.removeEventListener("submit", handleSigninEvent);
        formElement.addEventListener("submit", handleSignupEvent);

        signupPromptFlag = true;
    }
    else{
        // console.log("Hit toggle Signup Prompt! Signup -> Signin");

        const titleElement = document.querySelector(".signin");
        titleElement.textContent = "會員登入";
        
        const formElement = document.querySelector("#signin_form");

        const nameIdElement = document.querySelector("#name_id");
        nameIdElement.remove();

        const signInButtonElement = document.querySelector("#signin_button");
        signInButtonElement.textContent = "登入";

        const signinTextElement = document.querySelector(".signup-text");
        signinTextElement.textContent = "新使用者，請 ";

        const promptElement = document.querySelector(".signup-container a");
        promptElement.textContent = "點此免費註冊";

        formElement.removeEventListener("submit", handleSignupEvent);
        formElement.addEventListener("submit", handleSigninEvent);

        signupPromptFlag = false;
    }
}


// signin/signup related functions and event handlers
async function signin(event){
    event.preventDefault;
    console.log("sign-in event listener triggered!");
    const signinFormData = {};
    signinFormData["email"] = document.querySelector("#username_id").value;
    signinFormData["password"] = document.querySelector("#password_id").value;
    // console.log(signinFormData);
    const signinResponse = await fetch("/api/user/auth",{
        method: "PUT",
        body: JSON.stringify(signinFormData),
        headers: new Headers({ "Content-Type":"application/json" })
    })
    const signinResponseJSON = await signinResponse.json();
    if (signinResponseJSON.error){
        console.log("Sign in unsuccessful.");
        const signinResponseElement = document.querySelector(".signin-response-text");
        signinResponseElement.textContent = "無法登入：" + signinResponseJSON.message;
        signinResponseElement.style.display = "block";
        setTimeout(() => signinResponseElement.style.display = "none", 3000);
        console.log(signinResponseJSON.message);
    }
    else if (signinResponseJSON.token){
        console.log("Successfully signed in!");
        window.localStorage.setItem('token', signinResponseJSON.token);

        const signinResponseElement = document.querySelector(".signin-response-text");
        signinResponseElement.textContent = "登入成功！即將導向至會員中心...";
        signinResponseElement.style.display = "block";
        setTimeout(() => window.location.href = "member", 3000);
    }
    else{
        //其他狀況暫放
        console.log("Unknown error, please notify admin to check logs");
    }
}

async function signup(e){
    e.preventDefault;
    // console.log("signup event listener triggered!");
    const signupFormData = {};
    signupFormData["email"] = document.querySelector("#username_id").value;
    signupFormData["password"] = document.querySelector("#password_id").value;
    signupFormData["name"] = document.querySelector("#name_id").value;

    // console.log(signupFormData);
    const signupResponse = await fetch("/api/user",{
        method: "POST",
        body: JSON.stringify(signupFormData),
        headers: new Headers({ "Content-Type":"application/json" })
    })
    signupResponseJSON = await signupResponse.json();
    if (signupResponseJSON.error){
        console.log("Got response from server: error when creating new user");
        const signupResponseElement = document.querySelector(".signin-response-text");
        signupResponseElement.textContent = "無法註冊：" + signupResponseJSON.message;
        signupResponseElement.style.display = "block";
        setTimeout(() => signupResponseElement.style.display = "none", 3000);
    }
    else if (signupResponseJSON.ok){
        console.log("Got response from server: new user successfully created!");
        const signupResponseElement = document.querySelector(".signin-response-text");
        signupResponseElement.textContent = "新會員註冊成功！請使用帳號密碼登入";
        signupResponseElement.style.display = "block";
        setTimeout(() => signupResponseElement.style.display = "none", 3000);
    }
    else{
        // other cases
        console.log("Unknown error, please notify admin to check logs");
    }
}

async function handleSigninEvent(event){
    event.preventDefault();  
    signinButton = document.querySelector("#signin_button");
    signinButton.disabled = true;
    await signin(event);
    setTimeout(() => signinButton.disabled = false, 3000);
}

async function handleSignupEvent(event){
    event.preventDefault();
    signinButton = document.querySelector("#signin_button");
    signinButton.disabled = true;
    await signup(event);
    setTimeout(() => signinButton.disabled = false, 3000);
}

// Initialize signin/signup button
async function initializeSignedInElements(tokenStatus){
    if (tokenStatus){
        // handle (remove) signin button
        let signinButton = document.querySelector("#signin-button");
        // signinButton.remove();
        signinButton.textContent = "登出系統";
        signinButton.addEventListener("click", (event) => {
            removeSigninToken();
        });
    }
    else{
        // when not logged in, handle signin button and booking button have same function (activate curtain).
        let signinButton = document.querySelector("#signin-button");
        signinButton.textContent = "登入/註冊";
        signinButton.addEventListener("click", activateCurtain);

        // adjust use_api behavior after signin is finished
        const uploadVideoButton = document.querySelector("#upload-video-button");
        uploadVideoButton.remove();
        const memberPageButton = document.querySelector("#member-page-button");
        memberPageButton.remove();

    }
}

function initializeStartHereElements(tokenStatus){
    const buttons = document.querySelectorAll("#start-here-button");
    if (tokenStatus){
        const startHereText1 = document.querySelector("#start-here-text-1");
        if (startHereText1){
            startHereText1.textContent = "點擊以下按鈕開始使用，或向下捲動以了解更多！";
        }
        const startHereText2 = document.querySelector("#start-here-text-2");
        if (startHereText2){
            startHereText2.textContent = "點擊以下按鈕，即可開始使用。";
        }
    
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].textContent = "開始使用";
            buttons[i].addEventListener("click", () => window.location.href="/upload_video");
        }
    }
    else{
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].textContent = "登入/註冊";
            buttons[i].addEventListener("click", activateCurtain);
        }
    }
}

function initializeSequenceGeneral(){
    addEventListener("DOMContentLoaded", async () => {
        const tokenStatus = await checkToken();
        console.log("Token status:", tokenStatus);
        initializeSignedInElements(tokenStatus);
        initializeStartHereElements(tokenStatus);
    })
}
initializeSequenceGeneral();