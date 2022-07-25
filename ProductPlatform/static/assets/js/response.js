'use strict';

//селекторы основных
let price_inp = document.querySelector('#price-suggestion');
let description_textarea = document.querySelector('#description');
let edit_btn = document.querySelector('#edit-btn');
let submit_btn = document.querySelector('#submit-btn');
let cancel_btn = document.querySelector('#cancel-btn');
let save_btn = document.querySelector('#save-btn');

function make_readonly() {
  if (
    price_inp.value !== '' &&
    description_textarea.value !== '' &&
    submit_btn.dataset.canceledresponse === 'false'
  ) {
    price_inp.setAttribute('readonly', 'readonly');
    price_inp.classList.add('read_only');
    description_textarea.setAttribute('readonly', 'readonly');
    description_textarea.classList.add('read_only');

    if (submit_btn) {
      submit_btn.style.display = 'none';
      edit_btn.style.display = 'block';
      edit_btn.addEventListener('click', () => {
        make_modifiable();
      });
    }
    cancel_btn.style.display = 'block';
  }
}

function make_modifiable() {
  save_btn.style.display = 'block';
  edit_btn.style.display = 'none';
  cancel_btn.style.display = 'none';
  price_inp.removeAttribute('readonly');
  price_inp.classList.remove('read_only');
  description_textarea.removeAttribute('readonly');
  description_textarea.classList.remove('read_only');
}

make_readonly();
