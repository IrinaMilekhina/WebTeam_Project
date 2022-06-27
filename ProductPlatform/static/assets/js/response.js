"use strict";

//селекторы основных
let company_inp = document.querySelector("#company");
let category_inp = document.querySelector("#category");
let price_inp = document.querySelector("#price-suggestion");
let description_textarea = document.querySelector("#description");
let edit_btn = document.querySelector("#edit-btn");
let submit_btn = document.querySelector("#submit-btn");
const responses = document.querySelector("#res");


function make_readonly() {
    if (price_inp.value !== '' && description_textarea.value !== '' && submit_btn.dataset.canceledresponse === "false") {
        price_inp.setAttribute("readonly", "readonly");
        price_inp.classList.add("read_only");
        description_textarea.setAttribute("readonly", "readonly");
        description_textarea.classList.add("read_only");

        submit_btn.style.display = "none";
        edit_btn.style.display = "block";
    }
}

function make_modifiable() {
    price_inp.removeAttribute("readonly");
    price_inp.classList.remove("read_only");
    description_textarea.removeAttribute("readonly");
    description_textarea.classList.remove("read_only");
}

category_inp.setAttribute("readonly", "readonly");
category_inp.classList.add("read_only");

make_readonly();