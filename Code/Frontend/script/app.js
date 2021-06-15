const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let htmlBew, htmlRook, htmlVent, htmlLamp, htmlBuzz, htmlTemp, htmlTabRook, htmlTabAlarm, htmlGewTemp, htmlInput, htmlSubmit;
let teller = 0;
let buzzer = 0;
let lamp = 0;

const clearClassList = function (el) {
  el.classList.remove('c-room--wait');
  el.classList.remove('c-room--on');
};

const listenToUI = function () {
  // htmlVent.addEventListener('click', function () {
  //   if (teller == 0) {
  //     teller = 1;
  //   } else {
  //     teller = 0;
  //   }
  //   socket.emit('F2B_vent_click', { stand: teller });
  // });

  htmlBuzz.addEventListener('click', function () {
    if (buzzer == 0) {
      buzzer = 1;
    } else {
      buzzer = 0;
    }
    socket.emit('F2B_buzzer_click', { stand: buzzer });
  });

  htmlLamp.addEventListener('click', function () {
    if (lamp == 0) {
      lamp = 1;
    } else {
      lamp = 0;
    }
    socket.emit('F2B_lamp_click', { stand: lamp });
  });
};

const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
  });
  socket.on('B2F_data_temp', function (jsonobject) {
    htmlTemp.innerHTML = `${jsonobject.temp}°C`;
  });
  socket.on('B2F_data_beweging', function (jsonobject) {
    if (jsonobject.beweging > 10) {
      htmlBew.innerHTML = `Er is beweging. Data sensor: ${jsonobject.beweging}`;
    } else {
      htmlBew.innerHTML = `Er is geen beweging. Data sensor: ${jsonobject.beweging}`;
    }
  });
  socket.on('B2F_data_rook', function (jsonobject) {
    htmlRook.innerHTML = `Rooksensor data = ${jsonobject.rook}`;
  });
  socket.on('B2F_data_tab_rook', function (jsonobject) {
    htmlString = '';
    for (const rook of jsonobject) {
      htmlString += `<table>
      <tr>
          <th>Rook</th>
          <th>${rook.tijd}</th>
      </tr>
  </table>`;
    }
    htmlTabRook.innerHTML = htmlString;
  });
  socket.on('B2F_data_tab_alarm', function (jsonobject) {
    htmlString = '';
    for (const alarm of jsonobject) {
      htmlString += `<table>
      <tr>
          <th>Alarm</th>
          <th>${alarm.tijd}</th>
      </tr>
  </table>`;
    }
    htmlTabAlarm.innerHTML = htmlString;
  });

  socket.on('B2F_data_gew_temp', function(jsonobject) {
    htmlGewTemp.innerHTML = `${jsonobject.waarde}`
    htmlInput.value = `${jsonobject.waarde}`
  })

  htmlSubmit.addEventListener('click', function() {
    waarde = htmlInput.value
    socket.emit('F2B_gew_temp', waarde)
    htmlGewTemp.innerHTML = `${waarde}`
  })
};

document.addEventListener('DOMContentLoaded', function () {
  htmlTemp = document.querySelector('.js-temp');
  htmlBew = document.querySelector('.js-bew');
  htmlRook = document.querySelector('.js-rook');
  htmlVent = document.querySelector('.js-vent');
  htmlBuzz = document.querySelector('.js-buzz');
  htmlLamp = document.querySelector('.js-lamp');
  htmlTabRook = document.querySelector('.js-tab--rook');
  htmlTabAlarm = document.querySelector('.js-tab--alarm');
  htmlGewTemp = document.querySelector('.js-gewTemp')
  htmlInput = document.querySelector('.js-input')
  htmlSubmit = document.querySelector('.js-submit')
  console.info('DOM geladen');
  listenToUI();
  listenToSocket();
});
