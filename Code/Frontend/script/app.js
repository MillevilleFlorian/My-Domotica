const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let htmlBew,htmlRook, htmlVent,htmlLamp, htmlBuzz, htmlTemp
let teller = 0
let buzzer = 0
let lamp = 0

const clearClassList = function (el) {
  el.classList.remove("c-room--wait");
  el.classList.remove("c-room--on");
};

const listenToUI = function () {
  htmlVent.addEventListener('click', function () {
    if (teller == 0) {
      teller = 1
    } else {
      teller = 0
    }
    socket.emit('F2B_vent_click', {'stand': teller})
  })

  htmlBuzz.addEventListener('click',function () {
    if (buzzer == 0) {
      buzzer = 1
    } else {
      buzzer = 0
    }
    socket.emit('F2B_buzzer_click', {'stand': buzzer})
  })

  htmlLamp.addEventListener('click',function () {
    if (lamp == 0) {
      lamp = 1
    } else {
      lamp = 0
    }
    socket.emit('F2B_lamp_click', {'stand': lamp})
  })
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
  socket.on("B2F_data_temp", function(jsonobject) {
    htmlTemp.innerHTML = `temperatuur = ${jsonobject.temp}°C`
  })
  socket.on("B2F_data_beweging", function(jsonobject) {
    if (jsonobject.beweging > 10){
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
  htmlTemp = document.querySelector('.js-temp')
  htmlBew = document.querySelector('.js-bew')
  htmlRook = document.querySelector('.js-rook')
  htmlVent = document.querySelector('.js-vent')
  htmlBuzz = document.querySelector('.js-buzz')
  htmlLamp = document.querySelector('.js-lamp')
  console.info("DOM geladen");
  listenToUI();
  listenToSocket();
});
