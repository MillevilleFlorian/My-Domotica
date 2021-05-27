const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let htmlBew,htmlRook

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
    let htmlTemp = document.getElementById('paragraph_temp')
    htmlTemp.innerHTML = `temperatuur = ${jsonobject.temp}°C`
  })
  socket.on("B2F_data_beweging", function(jsonobject) {
    if (jsonobject.beweging > 10){
      let htmlBew = document.getElementById('paragraph_bew')
      htmlBew.innerHTML = `Er is beweging. Data sensor: ${jsonobject.beweging}`
    }else{
      htmlBew.innerHTML = `Er is geen beweging. Data sensor: ${jsonobject.beweging}`
    }
  })
  socket.on('B2F_data_rook', function(jsonobject) {
    htmlRook.innerHTML = `Rooksensor data = ${jsonobject.rook}`
  })
};

document.addEventListener("DOMContentLoaded", function () {
  htmlBew = document.getElementById('paragraph_bew')
  htmlRook = document.getElementById('paragraph_rook')
  console.info("DOM geladen");
  listenToUI();
  listenToSocket();
});
