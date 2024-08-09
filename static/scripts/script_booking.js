function renderBookingData(bookingStatusJson){
    //有種可以簡化為神秘迴圈的感覺

    console.log("Rendering booking data...");
    if (!bookingStatusJson.data){
        // console.log("Fetched data says there is no booking!!!!!");        
        const bookingMainContainer = document.querySelector(".booking-main-container");
        const noBookingText = document.createElement("div");
        noBookingText.classList = "booking-text body gray-70";
        noBookingText.textContent = "目前沒有任何待預訂的行程";
        const bookingForm = document.querySelector("#booking-form-id");
        bookingMainContainer.insertBefore(noBookingText, bookingForm);
        return false;
    }
    else{
        const bookingMainContainer = document.querySelector(".booking-main-container");
        const bookingAttractionContainer = document.createElement("div");
        bookingAttractionContainer.classList = "booking-attraction-container";
        
        const bookingForm = document.querySelector("#booking-form-id");
        bookingMainContainer.insertBefore(bookingAttractionContainer, bookingForm);

        // image
        const bookingAttractionImageContainer = document.createElement("div");
        bookingAttractionImageContainer.classList = "booking-attraction-image-container";
        const bookingAttractionImage = document.createElement("img");
        bookingAttractionImage.classList = "booking-attraction-image";
        // SQL returns only 1 image so the first image is used
        bookingAttractionImage.src = bookingStatusJson.data.attraction.image;
        bookingAttractionImageContainer.appendChild(bookingAttractionImage);
        bookingAttractionContainer.appendChild(bookingAttractionImageContainer);

        // text div
        const bookingAttractionText = document.createElement("div");
        bookingAttractionText.classList = "booking-attraction-text";
        bookingAttractionContainer.appendChild(bookingAttractionText);

        // attraction name
        const bookingAttractionTextAttractionOuter = document.createElement("div");
        bookingAttractionTextAttractionOuter.classList = "body bold cyan-70";
        bookingAttractionTextAttractionOuter.textContent = "台北一日遊：";
        const bookingAttractionTextAttractionInner = document.createElement("span");
        bookingAttractionTextAttractionInner.classList = "booking-attraction-content body bold";
        bookingAttractionTextAttractionInner.id = "booking-name";
        bookingAttractionTextAttractionInner.textContent = bookingStatusJson.data.attraction.name;

        // attraction date
        const bookingAttractionTextDateOuter = document.createElement("div");
        bookingAttractionTextDateOuter.classList = "body bold gray-70";
        bookingAttractionTextDateOuter.textContent = "日期：";
        const bookingAttractionTextDateInner = document.createElement("span");
        bookingAttractionTextDateInner.classList = "booking-attraction-content body";
        bookingAttractionTextDateInner.id = "booking-date";
        bookingAttractionTextDateInner.textContent = bookingStatusJson.data.date;

        // attraction time
        const bookingAttractionTextTimeOuter = document.createElement("div");
        bookingAttractionTextTimeOuter.classList = "body bold gray-70";
        bookingAttractionTextTimeOuter.textContent = "時間：";
        const bookingAttractionTextTimeInner = document.createElement("span");
        bookingAttractionTextTimeInner.classList = "booking-attraction-content body";
        bookingAttractionTextTimeInner.id = "booking-time";
        bookingAttractionTextTimeInner.textContent = bookingStatusJson.data.time === "morning" ? "上半天" : "下半天";

        // attraction price
        const  bookingAttractionTextPriceOuter = document.createElement("div");
        bookingAttractionTextPriceOuter.classList = "body bold gray-70";
        bookingAttractionTextPriceOuter.textContent = "費用：";
        const bookingAttractionTextPriceInner = document.createElement("span");
        bookingAttractionTextPriceInner.classList = "booking-attraction-content body";
        bookingAttractionTextPriceInner.id = "booking-price";
        bookingAttractionTextPriceInner.textContent = "新台幣" + bookingStatusJson.data.price + "元";

        // attraction address
        const bookingAttractionTextAddressOuter = document.createElement("div");
        bookingAttractionTextAddressOuter.classList = "body bold gray-70";
        bookingAttractionTextAddressOuter.textContent = "地點：";
        const bookingAttractionTextAddressInner = document.createElement("span");
        bookingAttractionTextAddressInner.classList = "booking-attraction-content body";
        bookingAttractionTextAddressInner.id = "booking-address";
        bookingAttractionTextAddressInner.textContent = bookingStatusJson.data.attraction.address;

        // append all newly created divs
        bookingAttractionText.appendChild(bookingAttractionTextAttractionOuter);
        bookingAttractionText.appendChild(bookingAttractionTextDateOuter);
        bookingAttractionText.appendChild(bookingAttractionTextTimeOuter);
        bookingAttractionText.appendChild(bookingAttractionTextPriceOuter);
        bookingAttractionText.appendChild(bookingAttractionTextAddressOuter);

        // append inner spans to outer divs
        bookingAttractionTextAttractionOuter.appendChild(bookingAttractionTextAttractionInner);
        bookingAttractionTextDateOuter.appendChild(bookingAttractionTextDateInner);
        bookingAttractionTextTimeOuter.appendChild(bookingAttractionTextTimeInner);
        bookingAttractionTextPriceOuter.appendChild(bookingAttractionTextPriceInner);
        bookingAttractionTextAddressOuter.appendChild(bookingAttractionTextAddressInner);

        // append delete button (the image url is in CSS)
        const bookingAttractionDeleteIconContainer = document.createElement("button");
        bookingAttractionDeleteIconContainer.classList = "booking-attraction-delete-icon";
        bookingAttractionDeleteIconContainer.addEventListener("click", deleteBooking);
        bookingAttractionContainer.appendChild(bookingAttractionDeleteIconContainer);

        // update total price
        const totalPriceText = document.querySelector("#total-price");
        totalPriceText.textContent = bookingStatusJson.data.price;

        return true;
    }
}

// get signed in user data (20240627 deprecate test)
// async function initializeSignedInUserData(){
//     signinData = await checkToken();
//     if (signinData){     
//         document.querySelector("#booking-name").textContent = signinData.name;
//         bookingStatusJson = await fetchBookingApi();
        
//         const renderResult = renderBookingData(bookingStatusJson);
//         if (renderResult){
//             document.querySelector("#booking-form-id").style.display = "block";
//         }
//     }
//     else{
//         alert("尚未登入，即將重新導向至首頁！");
//         window.location.pathname = "/";
//     } 
// }

// initializeSignedInUserData();

// get signed in user data
async function initializeSignedInUserDataNew(tokenStatus){
    if (tokenStatus){     
        document.querySelector("#booking-name").textContent = tokenStatus.name;
        bookingStatusJson = await fetchBookingApi();
        
        const renderResultBool = renderBookingData(bookingStatusJson);
        if (renderResultBool){
            document.querySelector("#booking-form-id").style.display = "block";
            return bookingStatusJson;
        }
        else {
            return false;
        }
    }
    else{
        // alert("尚未登入，即將重新導向至首頁！");
        window.location.pathname = "/";
        return false;
    } 
}

// fetch booking API
async function fetchBookingApi(){
    let signinStatusToken = window.localStorage.getItem('token');
    bookingStatus = await fetch("./api/booking",{
        method: "get",        
        headers: {Authorization: `Bearer ${signinStatusToken}`}
    });
    bookingStatusJson = await bookingStatus.json();
    console.log(bookingStatusJson);
    return bookingStatusJson;
}

// fetch deleteBooking API
async function deleteBooking(){
    let confirmDelete = confirm("是否確認刪除此預定行程？");
    if (!confirmDelete){
        return false;
    }
    else{
        let signinStatusToken = window.localStorage.getItem('token');
        deleteStatus = await fetch("./api/booking",{
            method: "delete",        
            headers: {Authorization: `Bearer ${signinStatusToken}`}
        });
        deleteStatusJson = await deleteStatus.json();
        console.log("Response from server:", deleteStatusJson);
        if (deleteStatusJson.error){
            console.log("Delete unsuccessful, message:", deleteStatusJson.message);
            bookingStatusTicker = document.querySelector("#booking-status-ticker");
            bookingStatusTicker.textContent = "刪除失敗，請再試一次或重新整理本頁";
            bookingStatusTicker.style.display = "block";            
            setTimeout(() => {
                bookingStatusTicker.textContent = "";
                bookingStatusTicker.style.display = "none";
            }, 2000);
        }
        else{        
            console.log("Delete successful! Refreshing in 2s...");
            bookingStatusTicker = document.querySelector("#booking-status-ticker");
            bookingStatusTicker.textContent = "已成功刪除！即將重新整理...";
            bookingStatusTicker.style.display = "block";
            setTimeout(() => window.location.reload(), 2000);
        }
        return deleteStatusJson;
    }
}


// handle error when email is invalid
function addBookingButtonListener(tokenStatus, bookingStatusJson){
    console.log("Entered addBookingButtonListener");
    console.log("Token:", tokenStatus);
    console.log("Booking:", bookingStatusJson);
    const bookingButton = document.querySelector("#confirm-booking-button");
    bookingButton.addEventListener("click", (event) => {
        event.preventDefault();
        console.log("Booking button clicked! Front end validations");

        if (!confirm("確定訂購此行程？")){
            return;
        }
        else if(!validateContactInfo()){
            console.log("Contact info validation unsuccessful");
            document.querySelector("#payment-status-ticker").textContent = "聯絡資料格式有誤或空白，請確認填入資料";
            document.querySelector("#payment-status-ticker").style.display = "block";
            return;
        }
        
        console.log("Booking:", bookingStatusJson);
        let orderBodyOld = {};
        orderBodyOld["order"] = {};
        orderBodyOld["order"]["price"] = bookingStatusJson.data.price;
        orderBodyOld["order"]["trip"] = bookingStatusJson.data;
        // deep copy here, need to delete a key for API input spec
        orderBody = JSON.parse(JSON.stringify(orderBodyOld));
        delete orderBody["order"]["trip"]["price"];
        console.log("New status of bookingStatusJson after Delete:", bookingStatusJson);
        orderBody["order"]["contact"] = {};
        orderBody["order"]["contact"]["name"] = document.querySelector("#contact-name").value;
        orderBody["order"]["contact"]["email"] = document.querySelector("#contact-email").value;
        orderBody["order"]["contact"]["phone"] = document.querySelector("#contact-phone").value;
        console.log("orderBody before adding prime:", orderBody);

        document.querySelector("#payment-status-ticker").textContent = "已傳送資訊至伺服器，請稍候...";
        document.querySelector("#payment-status-ticker").style.display = "block";
        //TODO: 讓按鈕失效

        // callback => write in async?
        TPDirect.card.getPrime(async function(result) {
            console.log(result);
            if (result.status !== 0) {
            console.error('getPrime error');
            document.querySelector("#payment-status-ticker").textContent = "付款資料錯誤，請確認各欄位皆有填寫， 並檢查橘/紅色標記的資料";
            document.querySelector("#payment-status-ticker").style.display = "block";
            return;
            }
            let prime = result.card.prime;
            console.log('getPrime success: ', prime);
            orderBody["prime"] = prime;
            // test for unsuccessful payment
            // orderBody["prime"] = "974a642f39cd6d505a21e463e964f59484c16e506a9891b8bade8a30b29b6134";
            console.log("即將送出orderBody:", orderBody);
            let signinStatusToken = window.localStorage.getItem('token');
            orderStatus = await fetch("./api/orders",{
                method: "post",        
                headers: {"Authorization": `Bearer ${signinStatusToken}`, "Content-Type": "application/json"},
                body: JSON.stringify(orderBody),
            });
            orderStatusJSON = await orderStatus.json();
            console.log("Got response from server:", orderStatusJSON);

            // error handling here
            // do front-end validation also!

            if (orderStatusJSON.error){
                console.log("Response unsuccessful", orderStatusJSON);
                document.querySelector("#payment-status-ticker").textContent = "預定未成功，請確認已完整輸入資料，或重新整理後再試一次";
                document.querySelector("#payment-status-ticker").style.display = "block";
                return;
            }

            if (orderStatusJSON.data.payment.status === 0){
                console.log("Payment succeeded, redirecting");
                document.querySelector("#payment-status-ticker").textContent = "付款成功！即將重新導向...";
                document.querySelector("#payment-status-ticker").style.display = "block";
                setTimeout(() => window.location.href="../thankyou?number="+orderStatusJSON.data.number, 3000);
            }
            else{
                console.log("Payment unsuccessful"); // modify below time
                document.querySelector("#payment-status-ticker").textContent = "預定成功但付款失敗，請確認資料後再試一次，或聯繫客服進行付款。訂單編號：" + orderStatusJSON.data.number;
                document.querySelector("#payment-status-ticker").style.display = "block";
            }

        });
    });
}

function addCreditCardInputFormatter(){
    // code from various websites and ChatGPT. very very clever...
    // 總之，每輸入一次就強制用運算過的結果覆蓋掉原本的輸入
    creditCardNumber = document.querySelector("#credit-card-number");
    creditCardExpiry = document.querySelector("#credit-card-expiry");
    // card number part
    creditCardNumber.addEventListener("input", (event) => {
        // define raw and formatted values. Regex /\D/g means all non-digit characters & all matches.
        let rawValue = event.target.value.replace(/\D/g, '');
        // define as a string
        let formattedValue = '';

        // calculate formatted value
        for (let i = 0; i < rawValue.length; i++) {
            if (i > 0 && i % 4 === 0) {
                formattedValue += ' ';
            }
            formattedValue += rawValue[i];
        }
        // replace what is in the input box with the formatted value after EVERY input action (including key press, backspace, delete, paste...)
        event.target.value = formattedValue;
        // this line for testing purposes only
        // console.log(rawValue, formattedValue);
    });

    // card expiry month part
    creditCardExpiry.addEventListener("input", (event) => {
        let expiryValue = event.target.value.replace(/\D/g, '');
        if (expiryValue.length > 2) {
            expiryValue = expiryValue.slice(0, 2) + '/' + expiryValue.slice(2, 4);
        }
    event.target.value = expiryValue;
    // this line for testing purposes only
    // console.log(expiryValue);
});
}
function validateName(inputName) {
    return inputName.trim().length >= 1;
}

function validateEmail(email) {
    const emailRegex = /^\S+@\S+\.\S+$/;
    return emailRegex.test(email);
}

function validateContactInfo(){
    contactName = document.querySelector("#contact-name").value;
    contactEmail = document.querySelector("#contact-email").value;
    contactPhone = document.querySelector("#contact-phone").value;
    console.log("Name validation:", validateName(contactName));
    console.log("Email validation:", validateEmail(contactEmail));
    console.log("Phone validation:", validateName(contactPhone));
    return (validateName(contactName) && validateEmail(contactEmail) && validateName(contactPhone));
}

function initializeSequenceBooking(){
    addEventListener("DOMContentLoaded", async () => {
        const tokenStatus = await checkToken();
        console.log("After DOMContentLoaded, token status:", tokenStatus);
        initializeSignedInElementsNew(tokenStatus);
        const bookingStatusJson = await initializeSignedInUserDataNew(tokenStatus);
        addBookingButtonListener(tokenStatus, bookingStatusJson);
        // addCreditCardInputFormatter();
    })
    // this space reserved for later
}
initializeSequenceBooking();