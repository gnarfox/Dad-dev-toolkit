document.addEventListener("DOMContentLoaded", () => {
    const flightForm = document.querySelector("form[action='/travel/']");
    if (flightForm) {
        flightForm.addEventListener("submit", (e) => {
            console.log("Flight form submitted!");
        });
    }
});
