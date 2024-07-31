document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    var formData = new FormData(this);
    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        console.log(data);
        // Handle success or error response here
        if (data.message === "Login successful") {
            // Redirect to page.html
            window.location.href = "page.html";
        } else {
            // Handle error
            // For example, display an error message to the user
            alert(data.error || "Login failed. Please try again.");
        }
    } catch (error) {
        console.error("Error:", error);
        // Handle error
        // For example, display an error message to the user
        alert("Login failed. Please try again later.");
    }
});
