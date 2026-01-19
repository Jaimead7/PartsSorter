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


import { showAlert } from './utils.js';


let ws;
let reconnectDelay = 10000;
let reconnectTimeout;
let alertBlock;


async function initWebSocket() {
    try {
        connectWebSocket(`ws://${window.location.host}/api/ws/image-stream/`);
    } catch (error) {
        console.error('Error connecting to the web socket:', error);
    }
}

function connectWebSocket(url) {
    ws = new WebSocket(url);

    ws.onopen = () => {
        try{
            alertBlock.remove();
        } catch {}
        console.log('Websocket connected.');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('New message received:', data);
        const originOptions = document.querySelectorAll('input[name="origin-filter-option"]');
        const noneChecked = Array.from(originOptions).every(checkbox => !checkbox.checked);
        const selectedOrigins = Array.from(originOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        switch (data.type) {
            case 'new-image':
                data.origin = data.origin ? data.origin : 'Unknown';
                if (selectedOrigins.includes(data.origin) || noneChecked) {
                    transferImages();
                    const nameElement = document.getElementById('img-0-name');
                    if (nameElement) {
                        nameElement.innerText = data.image_url.split('/').pop() || 'Unknown';
                    }
                    const imgAlt = document.getElementById(`img-0-alt`);
                    if (imgAlt) {
                        imgAlt.hidden = true;
                    }
                    const img = document.getElementById('img-0-img');
                    if (img) {
                        img.src = `/api/${data.image_url}`;
                        img.hidden = false;
                    }
                    writeImageInfo(
                        data.origin,
                        'img-0-origin',
                        data.insp_result,
                        'img-0-type',
                        (data.trust * 100).toFixed(2) + '%',
                        'img-0-trust',
                        data.model,
                        'img-0-model'
                    )
                }
        }
    };

    ws.onerror = () => {
        console.error('Connection error');
        scheduleReconnect();
    };

    ws.onclose = () => {
        console.warn('Websocket disconnected');
        scheduleReconnect();
    };
}

function scheduleReconnect() {
    showAlert('Reconnecting to server...', 'warning', 4);
    clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(() => {
        initWebSocket();
    }, reconnectDelay);
}

function clearImages() {
    for (let i = 4; i >= 0; i--) {
        const img = document.getElementById(`img-${i}-img`);
        if (img) {
            img.src = '';
            img.hidden = true;
        }
        const imgAlt = document.getElementById(`img-${i}-alt`);
        if (imgAlt) {
            imgAlt.hidden = false;
        }
        clearImageInfo(i);
    }
}

function transferImages() {
    for (let i = 4; i > 0; i--) {
        try {
            transferImage(i-1, i);
            transferText(`img-${i-1}-name`, `img-${i}-name`);
            transferText(`img-${i-1}-origin`, `img-${i}-origin`);
            transferText(`img-${i-1}-type`, `img-${i}-type`);
            transferText(`img-${i-1}-trust`, `img-${i}-trust`);
            transferText(`img-${i-1}-model`, `img-${i}-model`);
        } catch (error) {}
    }
}

function transferImage(idOrigin, idDestiny) {
    const imgDestiny = document.getElementById(`img-${idDestiny}-img`)
    const spanDestiny = document.getElementById(`img-${idDestiny}-alt`)
    const imgOrigin = document.getElementById(`img-${idOrigin}-img`)
    const spanOrigin = document.getElementById(`img-${idOrigin}-alt`)

    if (!imgDestiny || !spanDestiny || !imgOrigin || !spanOrigin) {
        console.error('No Image Elements found.');
        return;
    }

    imgDestiny.src = imgOrigin.getAttribute('src') === '' ? '' : imgOrigin.getAttribute('src');
    imgDestiny.hidden = imgDestiny.getAttribute('src') === '';
    spanDestiny.hidden = imgDestiny.getAttribute('src') !== '';
}

function transferText(idOrigin, idDestiny) {
    const originElement = document.getElementById(idOrigin);
    const destinyElement = document.getElementById(idDestiny)

    if (!originElement || !destinyElement) {
        console.error('No Text Elements found.');
        return;
    }

    destinyElement.textContent = originElement.textContent;
}

function writeImageInfo(
    origin,
    originElementName,
    type,
    typeElementName,
    trust,
    trustElementName,
    model,
    modelElementName
) {
    let element = document.getElementById(originElementName);
    if (element) {
        element.innerText = origin;
    }
    element = document.getElementById(typeElementName);
    if (element) {
        element.innerText = type;
    }
    element = document.getElementById(trustElementName);
    if (element) {
        element.innerText = trust;
    }
    element = document.getElementById(modelElementName);
    if (element) {
        element.innerText = model;
    }
}

function clearImageInfo(id) {
    const originElement = document.getElementById(`img-${id}-origin`);
    if (originElement) {
        originElement.innerText = originElement.getAttribute('data-default-text')
    }
    const typeElement = document.getElementById(`img-${id}-type`);
    if (typeElement) {
        typeElement.innerText = typeElement.getAttribute('data-default-text')
    }
    const trustElement = document.getElementById(`img-${id}-trust`);
    if (trustElement) {
        trustElement.innerText = trustElement.getAttribute('data-default-text')
    }
}


export { initWebSocket };
