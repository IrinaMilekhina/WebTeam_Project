//Скрипт для работы с Доской заказа

const button_choice = document.querySelector('#choice_category');
const dropdown = document.querySelector('.dropdown-menu2');
const input_choice = document.querySelector('#search');
const filter_category = document.querySelectorAll('.meeting-table-row');

button_choice.addEventListener('click', () => show_hidden_menu());
input_choice.addEventListener('keyup', () => search_category());
input_choice.addEventListener('keydown', function (event) {
  if (event.keyCode === 13) {
    event.preventDefault();
  }
});

function show_hidden_menu() {
  if (window.getComputedStyle(dropdown).display === 'none') {
    dropdown.style.display = 'block';
    all_category();
  } else {
    dropdown.style.display = 'none';
  }
}

function search_category() {
  filter_category.forEach((element) => {
    if (
      element.childNodes[5].textContent
        .toLowerCase()
        .includes(input_choice.value)
    ) {
      element.style.display = 'table-row';
    } else {
      element.style.display = 'none';
    }
  });
}

function all_category() {
  dropdown.addEventListener('click', (e) => {
    var category = e.target.dataset['f'];
    dropdown.style.display = 'none';
    input_choice.value = 'Выбрана категория: ' + category;
    if (category == 'Все категории') {
      filter_category.forEach((element) => {
        element.style.display = 'table-row';
      });
    } else {
      filter_category.forEach((element) => {
        if (category != element.childNodes[5].textContent) {
          element.style.display = 'none';
        } else {
          element.style.display = 'table-row';
        }
      });
    }
  });
}
