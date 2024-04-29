function toggleMenu() {
    var menuTable = document.getElementById("menu-table");
    if (menuTable.style.display === "none") {
        menuTable.style.display = "table";
    } else {
        menuTable.style.display = "none";
    }
}

function updateMenu() {
    var selectedItems = document.querySelectorAll('input[name="selected_items[]"]:checked');
    var menuTableBody = document.getElementById("menu-table-body");
    menuTableBody.innerHTML = "";

    selectedItems.forEach(function(item) {
        var row = document.createElement("tr");
        var itemName = document.createElement("td");
        itemName.textContent = item.value;
        var itemPrice = document.createElement("td");
        itemPrice.textContent = item.getAttribute("data-price");
        row.appendChild(itemName);
        row.appendChild(itemPrice);
        menuTableBody.appendChild(row);
    });

    var quantityFields = document.getElementById("quantity-fields");
    quantityFields.innerHTML = "";

    selectedItems.forEach(function(item) {
        var quantityField = document.createElement("div");
        quantityField.className = "form-group";
        quantityField.innerHTML = "<label for='" + item.value + "'>Quantity for " + item.value + ":</label>" +
            "<input type='number' name='quantities[" + item.value + "]' id='" + item.value + "' class='form-control' min='1' required>";
        quantityFields.appendChild(quantityField);
    });

    var quantityForm = document.getElementById("quantity-form");
    if (selectedItems.length > 0) {
        quantityForm.style.display = "block";
    } else {
        quantityForm.style.display = "none";
    }
}