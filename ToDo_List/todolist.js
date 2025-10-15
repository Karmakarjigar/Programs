document.getElementById('AddItemBtn').addEventListener('click', function (event) {
    const data = document.getElementById('AddItemTextBox').value.trim()
    console.log(document.getElementById('AddItemTextBox').value)
    const keyName = 'itemId' + (document.querySelectorAll('#todoItems > .data').length + 1);
    const item = `<br>
    <div class="data">
        <input type="checkbox"  class="itemCheckbox" id="${keyName}">
        ${data}
        <span>❌</span>
    </div>`;
    document.getElementById('todoItems').innerHTML += item;
    document.getElementById('AddItemTextBox').value = '';


    registerCheckboxEvent(document.getElementById(keyName));
})

document.querySelectorAll(".itemCheckbox").forEach((element) => {
    registerCheckboxEvent(element)
});

function registerCheckboxEvent(element) {
    console.log(element, 'element');
    
    element.addEventListener('change', function(event) {
        const item = this.parentNode;
        
        console.log(3434);
        if (this.checked) {
            
            item.classList.add('strikethrough');
        } else {
            item.classList.remove('strikethrough');
        }
    });
}
