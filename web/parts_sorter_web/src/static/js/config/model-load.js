// MIT License

// Copyright (c) 2025 Jaime Álvarez Díaz
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the “Software”), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do
// so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
// COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
// IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
// CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import { showAlert } from '../utils.js';

const form = document.getElementById('modelLoadForm');
const loadButton = form?.querySelector('button[type="submit"]');
const resetButton = form?.querySelector('button[type="reset"]');

resetButton?.addEventListener('click', (event) => {
    event.preventDefault();
    window.location.replace('/config/models/');
});

loadButton?.addEventListener('click', async function(event) {
    event.preventDefault();

    const endpoint = `/api/model/`;
    const fileInput = document.getElementById('modelFile');
    const file = fileInput.files[0];
    const spinner = document.getElementById('submitSpinner');
    const label = document.getElementById('submitLabel');

    label.innerText = 'Loading...';
    spinner.removeAttribute('hidden');
    this.disabled = true;

    if (!file) {
        showAlert('Select a file', 'warning', 2);
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    let content = {
        method: 'POST',
        headers: {
            'accept': 'application/json',
        },
        body: formData
    }

    fetch(endpoint, content)
    .then(response => {
        if (response.ok) {
            window.location.replace('/config/models/');
        } else {
            throw new Error(`Error on server response (${response.status}) ${response.statusText}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error creating model: ' + error.message, 'danger', 2);
    })
    .finally(() => {
        label.innerText = 'Load';
        spinner.setAttribute('hidden', true);
        this.disabled = false;
    });

});