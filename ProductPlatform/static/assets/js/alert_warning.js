let errors = document.querySelector("#error-list");
let close_button = document.querySelector("#close-btn");

close_button.addEventListener("click",  () => {
  errors.style.display = "none";
});