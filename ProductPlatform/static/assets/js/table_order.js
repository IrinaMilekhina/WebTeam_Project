//Скрипт доски заказов
var category = document.querySelector('#id_category');
var sort_name = document.querySelector('#id_ordering_category');
var form = document.querySelector('.filter-form');
sort_name.addEventListener('change', () => {
  form.submit();
});
category.addEventListener('change', () => {
  form.submit();
});
