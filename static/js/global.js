
document.addEventListener("DOMContentLoaded", function() {
    // Set a timeout of 3 seconds (3000ms) for the fade out
    setTimeout(function() {
        // Select all flash messages
        var flashMessages = document.querySelectorAll(".flash-message");
        flashMessages.forEach(function(msg) {
            // Add the fade-out class to initiate the opacity transition
            msg.classList.add("fade-out");
            
            // Optionally, remove the element after the transition has completed (e.g., after 2 seconds)
            setTimeout(function() {
                if (msg && msg.parentNode) {
                    msg.parentNode.removeChild(msg);
                }
            }, 2000); // Adjust this duration if needed to match the CSS transition
        });
    }, 1000); // 3000 ms = 3 seconds
});