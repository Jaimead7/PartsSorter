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


let ws;
let reconnectDelay = 10000;
let reconnectTimeout;
let alertBlock;


async function initWebSocket() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        connectWebSocket(`ws://${config.ip}/ws/image-stream`);
    } catch (error) {
        console.error('Error loading config:', error);
        connectWebSocket('ws://localhost:8000/ws/image-stream');
    }
}

function connectWebSocket(url) {
    ws = new WebSocket(url);

    ws.onopen = () => {
        try{
            alertBlock.remove();
        } catch {}
        console.log("Websocket connected");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("New message received:", data);
        const originOptions = document.querySelectorAll('input[name="origin-filter-option"]');
        const noneChecked = Array.from(originOptions).every(checkbox => !checkbox.checked);
        const selectedOrigins = Array.from(originOptions)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        switch (data.type) {
            case "new-image":
                if (selectedOrigins.includes(data.origin) || noneChecked) {
                    transferImages();
                    document.getElementById("img-0-alt").hidden = true;
                    img = document.getElementById("img-0-img");
                    img.src = data.image_url;
                    img.hidden = false;
                    writeImageInfo(
                        data.origin,
                        "img-0-origin",
                        data.insp_result,
                        "img-0-type",
                        (data.trust * 100).toFixed(2) + '%',
                        "img-0-trust",
                        data.model,
                        "img-0-model"
                    )
                }
        }
    };

    ws.onerror = () => {
        console.error("Connection error");
        scheduleReconnect();
    };

    ws.onclose = () => {
        console.warn("Websocket disconnected");
        scheduleReconnect();
    };
}

function scheduleReconnect() {
    showAlert("Reconnecting to server...", "warning");
    clearTimeout(reconnectTimeout);
    reconnectTimeout = setTimeout(() => {
        initWebSocket();
    }, reconnectDelay);
}

function showAlert(message, type) {
    try {
        alertBlock.remove();
    } catch (error) {}
    alertBlock = document.createElement("dialog");
    alertBlock.className = `d-inline-block position-absolute top-2 end-0 alert alert-${type} m-0`;
    alertBlock.textContent = message;
    document.getElementById("main-content").appendChild(alertBlock);
}

function clearImages() {
    for (let i = 4; i >= 0; i--) {
        img = document.getElementById(`img-${i}-img`);
        img.src = "";
        img.hidden = true;
        document.getElementById(`img-${i}-alt`).hidden = false;
        clearImageInfo(i)
    }
}

function transferImages() {
    for (let i = 4; i > 0; i--) {
        try {
            transferImage(i-1, i);
            transferText(`img-${i-1}-origin`, `img-${i}-origin`);
            transferText(`img-${i-1}-type`, `img-${i}-type`);
            transferText(`img-${i-1}-trust`, `img-${i}-trust`);
            transferText(`img-${i-1}-model`, `img-${i}-model`);
        } catch (error) {}
    }
}

function transferImage(idOrigin, idDestiny) {
    imgDestiny = document.getElementById(`img-${idDestiny}-img`)
    spanDestiny = document.getElementById(`img-${idDestiny}-alt`)
    imgOrigin = document.getElementById(`img-${idOrigin}-img`)
    spanOrigin = document.getElementById(`img-${idOrigin}-alt`)
    imgDestiny.src = imgOrigin.getAttribute('src') === '' ? "" : imgOrigin.getAttribute('src');
    imgDestiny.hidden = imgDestiny.getAttribute('src') === '';
    spanDestiny.hidden = imgDestiny.getAttribute('src') !== '';
}

function transferText(idOrigin, idDestiny) {
    document.getElementById(idDestiny).textContent = document.getElementById(idOrigin).textContent;
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
    document.getElementById(originElementName).innerText = origin
    document.getElementById(typeElementName).innerText = type
    document.getElementById(trustElementName).innerText = trust
    document.getElementById(modelElementName).innerText = model
}

function clearImageInfo(id) {
    const originElement = document.getElementById(`img-${id}-origin`);
    if (originElement) {
        originElement.innerText = originElement.getAttribute("data-default-text")
    }
    const typeElement = document.getElementById(`img-${id}-type`);
    if (typeElement) {
        typeElement.innerText = typeElement.getAttribute("data-default-text")
    }
    const trustElement = document.getElementById(`img-${id}-trust`);
    if (trustElement) {
        trustElement.innerText = trustElement.getAttribute("data-default-text")
    }
}
