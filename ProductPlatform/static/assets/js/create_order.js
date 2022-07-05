// Скрипт очистки формы

var name_list = [
  'id_category',
  'id_name',
  'id_end_time',
  'id_description',
  'button_clear',
];

for (var i = 0; i < name_list.length; i++) {
  name_list[i] = document.querySelector('#' + name_list[i]);
}
name_list[4].addEventListener('click', () => all_fields_clear());

function all_fields_clear() {
  for (var i = 0; i < name_list.length - 1; i++) {
    name_list[i].value = '';
  }
}
