
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

function parseRewardString(rewardStr) {
    if (!rewardStr) return "";
    
    // Remove any extra spaces.
    rewardStr = rewardStr.trim();
    
    // Split reward parts by the ampersand (&)
    // Expecting format like: "Resources.Money = 1000 & Resources.Diamond = 5"
    var parts = rewardStr.split("&");
    
    // Mapping resource/unit keys to icon and label.
    var rewardMapping = {
      "Resources.Money":   { icon: "💵", label: "Money" },
      "Resources.Stone":   { icon: "🪨", label: "Stone" },
      "Resources.Iron":    { icon: "🔗", label: "Iron" },
      "Resources.Gold":    { icon: "🟡", label: "Gold" },
      "Resources.Diamond": { icon: "💎", label: "Diamond" },
      "Resources.Wood":    { icon: "🪵", label: "Wood" },
      "Resources.Wheat":   { icon: "🌾", label: "Wheat" },
      
      // Extra keys:
      "Units.Archer":      { icon: "🏹", label: "Archer" },
      "Units.Horse":       { icon: "🐎", label: "Horse" },
      "Units.Soldier":     { icon: "🗡️", label: "Soldier" },
      "Units.Boat":        { icon: "⛵", label: "Boat" },
      "Units.Duke":        { icon: "🤴", label: "Duke" }
    };
    
    var htmlParts = [];
    
    parts.forEach(function(part) {
      // Split each part by "=".
      var subParts = part.split("=");
      if (subParts.length === 2) {
        var key = subParts[0].trim();
        var value = subParts[1].trim();
        // Check if the key exists in our mapping.
        if (rewardMapping.hasOwnProperty(key)) {
          var icon = rewardMapping[key].icon;
          var label = rewardMapping[key].label;
          htmlParts.push("<span class='reward-item'>" + icon + " " + label + ": " + value + "</span>");
        } else {
          // Fallback in case key is unknown.
          htmlParts.push("<span class='reward-item'>" + key + ": " + value + "</span>");
        }
      }
    });
    
    return htmlParts.join(" ");
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    // Process reward elements after the DOM loads.
    var rewardElements = document.querySelectorAll(".quest-reward");
    
    rewardElements.forEach(function(elem) {
      var rewardStr = elem.getAttribute("data-reward");
      var parsedHTML = parseRewardString(rewardStr);
      // Overwrite the innerHTML so that it reads "Reward:" followed by the formatted rewards.
      elem.innerHTML = "Reward: " + parsedHTML;
    });
  });


document.addEventListener("DOMContentLoaded", function() {
    var scrollPos = sessionStorage.getItem("scrollPos");
    if (scrollPos) {
        window.scrollTo(0, parseInt(scrollPos, 10));
    }
});

// Save the scroll position in sessionStorage when the user scrolls
window.addEventListener("scroll", function() {
    sessionStorage.setItem("scrollPos", window.scrollY);
});