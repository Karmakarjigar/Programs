document.getElementById('AddItemBtn').addEventListener('click', function (event) {
    const data = document.getElementById('AddItemTextBox').value.trim()
    console.log(document.getElementById('AddItemTextBox').value)
    const item = `
                    <br>
                        <div class="data">
                        <label for="input1">
                            <input type="checkbox" id="inuput1">
                        </label>
                        ${data}
                        <span>❌</span>
                    </div>
    `
    document.getElementById('todoItems').innerHTML += item;
    document.getElementById('AddItemTextBox').value = '';
})

document.querySelectorAll(".input .checkbox").forEach((element) => {
    element.addEventListener('click', function(event) {
        const item = this.parentNode;

        if (this.checked) {
            item.classList.add('strikethrough');
        } else {
            item.classList.remove('strikethrough');
        }
    });
});