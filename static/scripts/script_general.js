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

// signout function
async function removeSigninToken(){
    localStorage.removeItem("token");
    // alert("您已成功登出！");
    window.location.reload();
}

// creates HTML elements of curtain and signin form
function createCurtainAndSigninForm(){    
    let curtainElement = document.createElement("div");
    curtainElement.classList = "curtain active";

    let signupSquareElement = document.createElement("div");
    signupSquareElement.classList="signup-form-bg";
    curtainElement.appendChild(signupSquareElement);

    let signupDecorationBarElement = document.createElement("div");
    signupDecorationBarElement.classList="decoration-bar";
    signupSquareElement.appendChild(signupDecorationBarElement);

    let buttonElement = document.createElement("button");
    buttonElement.classList="deactivate-curtain-button";
    buttonElement.addEventListener("click", (event) => {
        deactivateCurtain();
    });
    signupSquareElement.appendChild(buttonElement);

    let signupTitleElement = document.createElement("div");
    signupTitleElement.classList="header-3 bold signin gray-70";
    signupTitleElement.textContent="登入會員帳號";
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
    inputUsernameElement.placeholder = "輸入電子信箱";
    formElement.appendChild(inputUsernameElement);

    let inputPasswordElement = document.createElement("input");
    inputPasswordElement.classList = "body";
    inputPasswordElement.type = "password";
    inputPasswordElement.name = "password_name"
    inputPasswordElement.id = "password_id";
    inputPasswordElement.placeholder = "輸入密碼";
    formElement.appendChild(inputPasswordElement);

    let signinButtonElement = document.createElement("button");
    signinButtonElement.classList = "btn";
    signinButtonElement.id = "signin_button";
    signinButtonElement.textContent="登入帳戶";
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
    signupPromptElement.textContent = "還沒有帳戶？";
    signupContainerElement.appendChild(signupPromptElement);

    let signupAnchorElement = document.createElement("a");
    signupAnchorElement.textContent="點此註冊";
    signupAnchorElement.href="#";
    signupAnchorElement.onclick= () => toggleSignupPrompt();
    signupContainerElement.appendChild(signupAnchorElement);
    
    let bodyElement = document.querySelector("body");
    bodyElement.appendChild(curtainElement);
}

// curtain element (signin/signup form) activation and deactivation
function activateCurtain2(event){
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
        titleElement.textContent = "註冊會員帳號";

        const formElement = document.querySelector("#signin_form");        
        const usernameIdElement = document.querySelector("#username_id");

        const newNameInputElement = document.createElement("input");
        newNameInputElement.type="text";
        newNameInputElement.name="name_name";
        newNameInputElement.id="name_id";
        newNameInputElement.placeholder="輸入姓名";
        newNameInputElement.classList="signup-input body";
        formElement.insertBefore(newNameInputElement, usernameIdElement);
        
        const signInButtonElement = document.querySelector("#signin_button");
        signInButtonElement.textContent = "註冊新帳戶";

        const signinTextElement = document.querySelector(".signup-text");
        signinTextElement.textContent = "已經有帳戶了？";

        const promptElement = document.querySelector(".signup-container a");
        promptElement.textContent = "點此登入";

        formElement.removeEventListener("submit", handleSigninEvent);
        formElement.addEventListener("submit", handleSignupEvent);

        signupPromptFlag = true;
    }
    else{
        // console.log("Hit toggle Signup Prompt! Signup -> Signin");

        const titleElement = document.querySelector(".signin");
        titleElement.textContent = "登入會員帳號";
        
        const formElement = document.querySelector("#signin_form");

        const nameIdElement = document.querySelector("#name_id");
        nameIdElement.remove();

        const signInButtonElement = document.querySelector("#signin_button");
        signInButtonElement.textContent = "登入帳號";

        const signinTextElement = document.querySelector(".signup-text");
        signinTextElement.textContent = "還沒有帳戶？";

        const promptElement = document.querySelector(".signup-container a");
        promptElement.textContent = "點此註冊";

        formElement.removeEventListener("submit", handleSignupEvent);
        formElement.addEventListener("submit", handleSigninEvent);

        signupPromptFlag = false;
    }
}


// signin/signup related functions and event handlers
async function signin(e){
    e.preventDefault;
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
    signinResponseJSON = await signinResponse.json();
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

        // test function to use cookies, it is NOT WORKING yet!
        // setCookie('token', signinResponseJSON.token, 7);

        const signinResponseElement = document.querySelector(".signin-response-text");
        signinResponseElement.textContent = "登入成功！即將重新整理畫面...";
        signinResponseElement.style.display = "block";
        setTimeout(() => window.location.reload(), 3000);
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
        //其他狀況暫放
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

// only on page load, initialize signin/signup button
async function initializeSignedInElements(){
    let tokenStatus = await checkToken();
    console.log("Signin status:", tokenStatus);
    if (tokenStatus){
        // handle signin button
        let signinButton = document.querySelector(".signin-button");
        signinButton.remove();
        const newButton = document.createElement("button");
        newButton.textContent = "登出系統";
        newButton.classList = "navbar-button gray-70 body";
        newButton.addEventListener("click", (event) => {
            removeSigninToken()
        });
        const buttonContainer = document.querySelector(".navbar-topright-container");
        buttonContainer.appendChild(newButton);

        // handle booking button. in this case, booking button has redirect function
        let bookingButton = document.querySelector(".booking-button-topright");
        bookingButton.addEventListener("click", (event) => {
            window.location.href = "/use_api";
        });

    }
    else{
        // when not logged in, handle signin button and booking button have same function (activate curtain).
        let signinButton = document.querySelector(".signin-button");
        signinButton.textContent = "登入/註冊";
        signinButton.addEventListener("click", activateCurtain2);
        
        // adjust use_api behavior after signin is finished
        let bookingButton = document.querySelector(".booking-button-topright");
        bookingButton.addEventListener("click", (event) => {
            window.location.href = "/use_api";
        });

        // handle booking button. in this case, booking button has the same function as signin/signup button
        // let bookingButton = document.querySelector(".booking-button-topright");
        // bookingButton.addEventListener("click", activateCurtain2);
    }
}

// only on page load, initialize signin/signup button  //20240627 without fetchingAPI
async function initializeSignedInElementsNew(tokenStatus){
    if (tokenStatus){
        // handle (remove) signin button
        let signinButton = document.querySelector(".signin-button");
        signinButton.remove();

        // handle (create) member button
        const newMemberButton = document.createElement("button");
        newMemberButton.textContent = "會員中心";
        newMemberButton.classList = "navbar-button gray-70 body";
        newMemberButton.addEventListener("click", (event) => {
            window.location.href = "/member";
        });
        const memberButtonContainer = document.querySelector(".navbar-topright-container");
        memberButtonContainer.appendChild(newMemberButton);

        // handle (create) signout button
        const newButton = document.createElement("button");
        newButton.textContent = "登出系統";
        newButton.classList = "navbar-button gray-70 body";
        newButton.addEventListener("click", (event) => {
            removeSigninToken()
        });
        const buttonContainer = document.querySelector(".navbar-topright-container");
        buttonContainer.appendChild(newButton);

        

        // handle booking button. in this case, booking button has redirect function
        let apiDocsButton = document.querySelector(".api-docs-button");
        apiDocsButton.addEventListener("click", (event) => {
            window.location.href = "/use_api";
        });

    }
    else{
        // when not logged in, handle signin button and booking button have same function (activate curtain).
        let signinButton = document.querySelector(".signin-button");
        signinButton.textContent = "登入/註冊";
        signinButton.addEventListener("click", activateCurtain2);

        // adjust use_api behavior after signin is finished
        let apiDocsButton = document.querySelector(".api-docs-button");
        apiDocsButton.addEventListener("click", (event) => {
            window.location.href = "/use_api";
        });

        // handle booking button. in this case, booking button has the same function as signin/signup button
        // let bookingButton = document.querySelector(".booking-button-topright");
        // bookingButton.addEventListener("click", activateCurtain2);

    }
}

// Initialize sequence, wait for DOMContentLoaded event //20240627 deprecation test
// function initializeSequenceGeneral(){
//     addEventListener("DOMContentLoaded", () => {
//         // add correct button (signin or signout) to DOM and their event listeners
//         initializeSignedInElements();
//     })
//     // this space reserved for later
// }
// initializeSequenceGeneral();

// test function: setCookie (This is for Week 5 discussion)
// function setCookie(name, value, days) {
//     let expires = "";
//     if (days) {
//         const date = new Date();
//         date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
//         expires = "; expires=" + date.toUTCString();
//     }
//     //check GPT log for more parameters, testing only
//     document.cookie = name + "=" + (value || "") + expires + "; path=/; secure; samesite=strict; HttpOnly";
//     document.cookie = name + "=" + (value || "") + expires + "; path=/";
// }

function initializeSequenceGeneral(){
    addEventListener("DOMContentLoaded", async () => {
        const tokenStatus = await checkToken();
        console.log("After DOMContentLoaded, token status:", tokenStatus);
        initializeSignedInElementsNew(tokenStatus);
    })
    // this space reserved for later
}
initializeSequenceGeneral();