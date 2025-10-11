console.log('Hello World');

document.getElementById('AddItemBtn').addEventListener('click', function (event) {
    const data = document.getElementById('AddItemTextBox').value.trim()
    console.log(document.getElementById('AddItemTextBox').value)
    const item = `<div class="data">
                    <label for="input1">
                        <input type="checkbox" id="inuput1">
                    </label>
                    ${data}
                    <span>❌</span>
                </div>`
    document.getElementById('todoItems').innerHTML += item;
})