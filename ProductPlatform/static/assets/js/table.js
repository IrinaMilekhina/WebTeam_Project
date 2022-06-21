"use strict";

let rows = [...document.getElementById("topsuppliers").rows];
let flag = false;

rows.forEach(row => {
    if (flag) {
        row.classList.add("table-row");
        flag = false;
    } else {
        flag = true;
    }
});