// Get attraction ID from the URL(window object)
let attractionId;
function getAttractionIdFromUrl(){
    let pathName = window.location.pathname;
    match = pathName.match(/attraction\/(.+?)(\/)?$/); //把pathname /attraction之後的字串取出來放在match[1]
    console.log("Reading and matching URL by Regex:", match);
    if (match && match[1]){
        attractionId = match[1];
    }
    else{
        console.log("Attraction number from URL not found.");
        window.location.pathname = "/";
    }
}

// Fetch any url and parse as json.
async function getAttractionData(url){
    try{
        console.log("Fetching URL:", url);
        const response = await fetch(url);
        const response_json = await response.json();
        return response_json;
    }
    catch(e){
        // Backend responds with 400 or 500 when error happens, so this part is not successfully triggered yet.
        console.log("Fetch failed due to the following error:", e);
        window.location.href = "/";
    }
}

// Fetch and render content based on attraction ID + base URL.
async function getAttractionPage(attractionId){
    let attractionurlBase = "/api/attraction/";
    response_json = await getAttractionData(attractionurlBase+attractionId);
    console.log("Obtained response:", response_json);

    // Error handling
    if (response_json.error){
        alert("錯誤："+ response_json.message);
        window.location.href = "/";
        return;
    }
    else if (!Object.keys(response_json.data).length){
        alert("景點無資料，請重新嘗試，如持續出現請聯繫系統管理員");
        window.location.href = "/";
        return;
    }
    else{
        // render page title text in broswer tab
        let attractionTitle = document.querySelector(".attraction-title");
        attractionTitle.textContent = response_json.data.name + " - WeHelp 台北一日遊";

        // render text in the lower div
        let descriptionDiv = document.querySelector(".attraction-description-text");
        descriptionDiv.textContent = response_json.data.description;
        let addressDiv = document.querySelector(".attraction-address-text");
        addressDiv.textContent = response_json.data.address;
        let transportDiv = document.querySelector(".attraction-transport-text");
        transportDiv.textContent = response_json.data.transport;

        // render text in the top-right div
        let attractionDiv = document.querySelector(".attraction-text");
        attractionDiv.textContent = response_json.data.name;
        let categorySpan = document.querySelector(".category-text");
        categorySpan.textContent = response_json.data.category;
        let mrtSpan = document.querySelector(".mrt-text");
        mrtSpan.textContent = response_json.data.mrt;

        // render images for image scroll
        console.log("Total images received:", response_json.data.images.length);

        // add arrows if > 1 picture
        if (response_json.data.images.length > 1){
            console.log("Adding arrows...");

            let pictureDiv = document.querySelector(".picture");
            let dotContainer = document.querySelector(".dot-button-container");

            const newLeftArrowImage = document.createElement("img");
            newLeftArrowImage.src="../static/images/button_left_noborder.png"
            const newLeftArrowButton = document.createElement("button");
            newLeftArrowButton.className = "attraction-scroll-btn left-btn";
            newLeftArrowButton.id = "attraction-scroll-left";
            newLeftArrowButton.addEventListener('click', function(){
                plusSlides(-1);
            });
            newLeftArrowButton.appendChild(newLeftArrowImage);
            pictureDiv.insertBefore(newLeftArrowButton, dotContainer);

            const newRightArrowImage = document.createElement("img");
            newRightArrowImage.src="../static/images/button_right_noborder.png"
            const newRightArrowButton = document.createElement("button");
            newRightArrowButton.className = "attraction-scroll-btn right-btn";
            newRightArrowButton.id = "attraction-scroll-right";
            newRightArrowButton.addEventListener('click', function(){
                plusSlides(1);
            });
            newRightArrowButton.appendChild(newRightArrowImage);
            pictureDiv.insertBefore(newRightArrowButton, dotContainer);
        }

        // add pictures
        for (let i=0; i<response_json.data.images.length;i++){
            // console.log("Preloading image...")
            // const preloadImage = new Image();
            // preloadImage.src = response_json.data.images[i];

            console.log("Loading image...");
            let pictureDiv = document.querySelector(".picture");
            const newPictureDiv = document.createElement("div");
            newPictureDiv.className = "slides-picture";
            const newPictureImg = document.createElement("img");
            newPictureImg.src = response_json.data.images[i];
            newPictureDiv.appendChild(newPictureImg);

            // console.log("Picture div check:", pictureDiv);
            // below method adds in the opposite order...
            // pictureDiv.prepend(newPictureDiv);
            
            // below method adds in the correct order
            let dotContainer = document.querySelector(".dot-button-container");
            pictureDiv.insertBefore(newPictureDiv, dotContainer);
            // console.log("Added picture div!");

            // Add selection dots
            const newDotSpan = document.createElement("span");
            newDotSpan.className = "dot-button";
            newDotSpan.addEventListener('click', function(){
                slideIndex = i;
                showSlides(slideIndex);
            });

            dotContainer.append(newDotSpan);
        }
        let pictureDiv = document.querySelector(".picture");
        console.log("picture div check:", pictureDiv);

        // // add booking button listener
        // const bookingButton = document.querySelector(".booking-button");
        // let tokenStatus = await checkToken();
        // console.log("Signin status:", tokenStatus);
        // if (tokenStatus){
        //     bookingButton.addEventListener("click", bookAttraction);
        // }
        // // else activateCurtain2 defined in script_general.js
        // else{
        //     bookingButton.addEventListener("click", (event) => {
        //         event.preventDefault();
        //         activateCurtain2();
        //     });
        // }
        
    }

}

// Show a particular slide
function showSlides(index){
    let slides = document.querySelectorAll(".slides-picture");
    let dots = document.querySelectorAll(".dot-button");
    let totalSlides = slides.length;

    // positive number for mod(n,m) when n<0 in JS: mod(n,m) = ((n % m) + m) % m
    // actually, this works for both negative AND positive values!
    index = ((index % totalSlides) + totalSlides) % totalSlides;

    // if (index < 0){
    //     // positive number for mod(n,m) when n<0 in JS: mod(n,m) = ((n % m) + m) % m
    //     index = ((index % totalSlides) + totalSlides) % totalSlides;
    // }
    // else if (index >= totalSlides){
    //     index %= totalSlides;
    // }
    // console.log("total slides:", totalSlides);
    // console.log("index:", index);

    for (slideNo = 0; slideNo < totalSlides; slideNo++){
        if (slideNo === index){
            slides[slideNo].classList.add("slides-active"); //add class
            // slides[slideNo].style.display = "block"; //backup
            dots[slideNo].className = "dot-button selected";
            console.log("Activating slide:", slideNo);
        }
        else{
            slides[slideNo].classList.remove("slides-active"); //remove class
            // slides[slideNo].style.display = "none";
            dots[slideNo].className = "dot-button";
        }
    }
}

// Left and Right Arrow buttons handling.
function plusSlides(number){
    slideIndex += number;
    console.log("Internal slide no.:", slideIndex);
    showSlides(slideIndex);
}

// Tour price toggle function. Now support fixed price only.
// If advanced pricing schema occurs in the future, edit the function behavior accordingly
function initializeTourPrice(){
    document.querySelector("#tour-price").textContent = "2000";

    document.querySelector("#morning").addEventListener("change", function(){
        if (this.checked){
            document.querySelector("#tour-price").textContent = "2000";
        }
    });
    
    document.querySelector("#afternoon").addEventListener("change", function(){
        if (this.checked){
            document.querySelector("#tour-price").textContent = "2500";
        }
    });    
}

// add booking button listener
function addBookingButtonListener(tokenStatus){
    const bookingButton = document.querySelector(".booking-button");
    if (tokenStatus){
        console.log("Added booking button event by token: book attraction");
        bookingButton.addEventListener("click", bookAttraction);
    }
    // else activateCurtain2 defined in script_general.js
    else{
        console.log("Added booking button event by token: activate curtain");
        bookingButton.addEventListener("click", (event) => {
            event.preventDefault();
            activateCurtain2();
        });
    }
}

async function bookAttraction(event){
    event.preventDefault();
    // get the json from the fields in page
    let bookingData = {};
    bookingData["attractionId"] = parseInt(attractionId);
    bookingData["date"] = document.querySelector("#travel_date").value;
    bookingData["time"] = document.querySelector("input[name=timeslot]:checked").value;
    bookingData["price"] = parseInt(document.querySelector("#tour-price").textContent);
    console.log("Booking data check:", bookingData);

    // check if all fields are entered
    const bookingDataisEmpty = !Object.values(bookingData).every(x => x !== null && x !== '');  
    console.log("Empty check:", bookingDataisEmpty);
    if (bookingDataisEmpty){
        alert("請填入所有欄位！");
        return false;
    }
    // fetch API
    else{
        let signinStatusToken = window.localStorage.getItem('token');
        const bookingResponse = await fetch ("/api/booking",{
            method: "post",
            body: JSON.stringify(bookingData),
            headers: new Headers({ "Content-Type":"application/json", "Authorization": `Bearer ${signinStatusToken}` })
        });
        const bookingResponseJson = await bookingResponse.json();
        console.log(bookingResponseJson);

        if (!bookingResponseJson.ok){
            console.log("Booking unsuccessful, error message:", bookingResponseJson.message);
            bookingStatusTicker = document.querySelector("#booking-status-ticker");
            bookingStatusTicker.textContent = "預訂失敗，請再試一次或重新整理本頁";
            bookingStatusTicker.style.display = "inline-block";            
            setTimeout(() => {
                bookingStatusTicker.textContent = "";
                bookingStatusTicker.style.display = "none";
            }, 2000);
            return false;
        }
        else{
            console.log("Booking Successful!");
            bookingStatusTicker = document.querySelector("#booking-status-ticker");
            bookingStatusTicker.textContent = "預訂成功！重新導向中...";
            bookingStatusTicker.style.display = "inline-block";
            setTimeout(() => window.location.pathname = "/booking", 2000);
            return true;
        }
    }
}

// Initialize Attraction Page DOM
async function initializeAttraction(attractionId){
    await getAttractionPage(attractionId);
    slideIndex = 0;
    showSlides(slideIndex);
}

let slideIndex;
// initializeAttraction();
// initializeTourPrice();

// 20240627 new initialize sequence (again...)

function initializeSequenceAttraction(){
    addEventListener("DOMContentLoaded", async () => {
        getAttractionIdFromUrl();
        const tokenStatus = await checkToken();
        console.log("After DOMContentLoaded, token status:", tokenStatus);
        // add correct button (signin or signout) to DOM and their event listeners
        initializeSignedInElementsNew(tokenStatus);
        addBookingButtonListener(tokenStatus);
        await initializeAttraction(attractionId);
        initializeTourPrice();
    })
    // this space reserved for later
}
initializeSequenceAttraction();


