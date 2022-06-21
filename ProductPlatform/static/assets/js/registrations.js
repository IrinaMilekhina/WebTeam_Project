var token = '717031cfefa2c8a91268cb1b7754a018e8bbd27c';
var url = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party';

//селекторы основных
const ogrn_button = document.querySelector('#button-addon');
const input_form = document.querySelector('#view_company');
const register_button = document.querySelector('#register_button');
var input_form_name = document.querySelector('#id_comp_name');
var input_form_city = document.querySelector('#id_city');
var message_text = document.querySelector('#message');
var input_ogrn = document.querySelector('#id_ogrn');
var group_input = document.querySelector('#orgn-group-input');

message('Введите 13 или 15 цифр.');

ogrn_button.addEventListener('click', () => {
  const ogrn_value = document.querySelector('#id_ogrn').value;
  if (ogrn_value.length == 13 || ogrn_value.length == 15) {
    var options = {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: 'Token ' + token,
      },
      body: JSON.stringify({ query: ogrn_value }),
    };
    fetch(url, options)
      .then((response) => response.text())
      .then((result) => get_data(result))
      .catch((error) => no_data());
  } else {
    message('Ошибка. Введите 13 или 15 цифр.', 'red');
  }
});

function message(message, color) {
  message_text.innerHTML = message;
  message_text.style.color = color;
}

function no_data() {
  input_form.style.display = 'none';
  register_button.style.display = 'none';
  message('Такой ОГРН (ЕГРИП) не существует.', 'red');
}

function get_data(result) {
  let res2 = JSON.parse(result);
  let res3 = res2['suggestions'][0];
  comp_name = res3['data']['name']['full_with_opf'];
  comp_name = comp_name.toLowerCase();
  city = res3['data']['address']['data']['city'];
  status_company = res3['data']['state']['status'];
  show_hide_input(comp_name, city, status_company);
}

function show_hide_input(comp_name, city, status_company) {
  if (status_company == 'ACTIVE') {
    input_form.style.display = 'block';
    input_form_name.value = comp_name[0].toUpperCase() + comp_name.slice(1);
    input_form_city.value = city;
    register_button.style.display = 'block';
    input_ogrn.setAttribute('readonly', 'readonly');
    ogrn_button.style.display = 'none';
    group_input.classList.add('read_only');
    group_input.classList.remove('group-input');
    message('Проверка ОГРН (ЕГРИП) пройдена.', 'green');
  } else {
    message(
      'Организация или ИП исключены из реестра, либо в стадии банкротства.',
      'red'
    );
  }
}