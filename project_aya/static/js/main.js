'use strict'

var timerId = 0, relX = 0, relY = 0,
    iso = {};

window.onload = function() {
  /*iso = new Isotope('.users-list', {
    itemSelector: '.user-card'
  });*/
  document.addEventListener("click", function (event) {
    clickHandler(event.target);
  });
  document.addEventListener("change", function (event) {
    changeHandler(event.target);
  });
}

function clickHandler(obj) {
  if (obj.classList[0] == 'user-tg') {
    obj.children[0].click();
  }
}
function changeHandler(obj) {
  if (obj.name == 'filter') {
    var filters = {};
    if (document.getElementById('city').selectedOptions[0].value != '') filters['city'] = document.getElementById('city').selectedOptions[0].value;
    if (document.getElementById('speciality').selectedOptions[0].value != '') filters['speciality'] = document.getElementById('speciality').selectedOptions[0].value;
    if (document.getElementById('experience').selectedOptions[0].value != '') filters['experience'] = document.getElementById('experience').selectedOptions[0].value;
    //iso.arrange({ filter: filters });
    ajaxGet(filters);
    if (obj.value == '') obj.selectedIndex = 0;
  }
}

function ajaxGet(params) {
  params['X-CSRFToken'] = getCookie('csrftoken');
  $.ajax({
    type: 'GET',
    url: 'user-filter',
    data: params,
    success: function (response) {
      document.getElementById('users-list').innerHTML = response
    },
    error: function (response) {
        console.log(response)
    }
  })
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
