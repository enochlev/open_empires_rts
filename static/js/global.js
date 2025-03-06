document.addEventListener("DOMContentLoaded", function() {

  /***********************/
  /*  FADE FLASH MESSAGES */
  /***********************/
  function fadeFlashMessages() {
      setTimeout(function() {
          const flashMessages = document.querySelectorAll(".flash-message");
          flashMessages.forEach(function(msg) {
              msg.classList.add("fade-out");
              setTimeout(function() {
                  if (msg.parentNode) {
                      msg.parentNode.removeChild(msg);
                  }
              }, 2000); // matches your CSS fade-out transition
          });
      }, 1000); // delay before fading begins
  }

  /***********************/
  /* RESTORE SCROLL POSITION */
  /***********************/
  function restoreScrollPosition() {
      const scrollPos = sessionStorage.getItem("scrollPos");
      if (scrollPos) {
          window.scrollTo(0, parseInt(scrollPos, 10));
      }
  }

  window.addEventListener("scroll", function() {
      sessionStorage.setItem("scrollPos", window.scrollY);
  });

  /***********************/
  /* SIMPLE TAB SWITCHING */
  /***********************/
  function showTab(tabName) {
    // Immediately store the active tab
    sessionStorage.setItem('activeTab', tabName);
    
    // Deactivate all tabs
    const tabs = document.querySelectorAll('.tab-header div[data-tab]');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Deactivate all content panes
    const panes = document.querySelectorAll('.tab-content .tab-pane');
    panes.forEach(pane => pane.classList.remove('active'));

    // Activate the target tab header
    const activeTabHeader = document.querySelector(`.tab-header div[data-tab="${tabName}"]`);
    if (activeTabHeader) activeTabHeader.classList.add('active');

    // Activate the target content pane
    const activePane = document.getElementById(`tab-${tabName}`);
    if (activePane) activePane.classList.add('active');
}

  function setupTabs() {
      const storedTab = sessionStorage.getItem('activeTab');
      let defaultTab = 'village'; // fallback/default tab

      if (storedTab && document.getElementById(`tab-${storedTab}`)) {
          defaultTab = storedTab;
      }

      // Set initially active tab on page load
      showTab(defaultTab);

      // Save active tab to sessionStorage on click
      const tabs = document.querySelectorAll('.tab-header div[data-tab]');
      tabs.forEach(tab => {
          tab.addEventListener('click', function() {
              sessionStorage.setItem('activeTab', this.getAttribute('data-tab'));
              showTab(this.getAttribute('data-tab'));
          });
      });
  }

  /***********************/
  /* TOGGLE QUEST PANEL */
  /***********************/
  function setupQuestToggle() {
      const toggleBtn = document.getElementById('quest-toggle-btn');
      const questPanel = document.getElementById('quest-panel');

      if (toggleBtn && questPanel) {
          toggleBtn.addEventListener('click', function() {
              if (questPanel.style.display === 'none' || questPanel.style.display === '') {
                  questPanel.style.display = 'block';
              } else {
                  questPanel.style.display = 'none';
              }
          });
      }
  }

  /***********************/
  /* PARSE REWARD STRINGS INTO HTML */
  /***********************/
  function parseRewardString(rewardStr) {
      if (!rewardStr) return "";
      rewardStr = rewardStr.trim();
      const rewardMapping = {
          "Resources.Money":   { icon: "💵", label: "Money" },
          "Resources.Stone":   { icon: "🪨", label: "Stone" },
          "Resources.Iron":    { icon: "🔗", label: "Iron" },
          "Resources.Gold":    { icon: "🟡", label: "Gold" },
          "Resources.Diamond": { icon: "💎", label: "Diamond" },
          "Resources.Wood":    { icon: "🪵", label: "Wood" },
          "Resources.Wheat":   { icon: "🌾", label: "Wheat" },
          "Units.Archer":      { icon: "🏹", label: "Archer" },
          "Units.Horse":       { icon: "🐎", label: "Horse" },
          "Units.Soldier":     { icon: "🗡️", label: "Soldier" },
          "Units.Boat":        { icon: "⛵", label: "Boat" },
          "Units.Duke":        { icon: "🤴", label: "Duke" }
      };

      return rewardStr.split("&").map(part => {
          const [keyRaw, valueRaw] = part.split("=");
          const key = keyRaw.trim();
          const value = valueRaw.trim();
          if (rewardMapping[key]) {
              const { icon, label } = rewardMapping[key];
              return `<span class='reward-item'>${icon} ${label}: ${value}</span>`;
          } else {
              return `<span class='reward-item'>${key}: ${value}</span>`;
          }
      }).join(" ");
  }

  function processQuestRewards() {
      const rewardElements = document.querySelectorAll(".quest-reward");
      rewardElements.forEach(elem => {
          const parsedHTML = parseRewardString(elem.getAttribute("data-reward"));
          elem.innerHTML = "Reward: " + parsedHTML;
      });
  }

  /***********************/
  /* INITIALIZE ALL FEATURES */
  /***********************/
  fadeFlashMessages();
  restoreScrollPosition();
  setupTabs();
  setupQuestToggle();
  processQuestRewards();

});