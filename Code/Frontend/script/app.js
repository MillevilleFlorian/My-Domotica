const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const clearClassList = function (el) {
  el.classList.remove("c-room--wait");
  el.classList.remove("c-room--on");
};

const listenToUI = function () {
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
  socket.on("B2F_data_temp", function(jsonobject) {
    let htmlTemp = document.getElementById('paragraph')
    htmlTemp.innerHTML = `temperatuur = ${jsonobject.temp}`
    // htmlTemp.innerHTML = `<p> temperatuur = ${jsonobject.temp}  </p>`
  })
};

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  listenToUI();
  listenToSocket();
});
