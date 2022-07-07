//Скрипт для автоматического поиска на страницы категории

'use strict';

let status = document.querySelector('#id_is_active');
let sort_name = document.querySelector('#id_ordering_category');
let form = document.querySelector('#categories_filter_form');

sort_name.addEventListener('change', () => {
  form.submit();
});

status.addEventListener('change', () => {
  form.submit();
});
