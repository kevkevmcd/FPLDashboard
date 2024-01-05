function showLoading() {
    var loadingSpinner = document.getElementById("loading-spinner");

    loadingSpinner.style.display = "block";
  }

function getRandomLoadingMessage() {
  const message_list = [
    "Please wait while we collect your league data...",
    "Hold on while we generate your league info...",
    "Assembling many tables, this may take a moment..."
  ];

  var message = message_list[Math.floor(Math.random() * message_list.length)];
  
  return message;
}