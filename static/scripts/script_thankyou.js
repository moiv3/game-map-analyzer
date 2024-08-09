function getBookingNumberFromUrl(){
    const url = new URL(window.location.href);
    const bookingNumber = url.searchParams.get("number");
    let textBox = document.querySelector(".thankyou-text");
    textBox.textContent = bookingNumber;
}

//initialize sequence here
function initializeSequenceThankyou(){
    addEventListener("DOMContentLoaded", async () => {
        const tokenStatus = await checkToken();
        console.log("After DOMContentLoaded, token status:", tokenStatus);
        initializeSignedInElementsNew(tokenStatus);        
        getBookingNumberFromUrl();
    })
}
initializeSequenceThankyou();