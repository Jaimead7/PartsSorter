// Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.


let ws;
let reconnectDelay = 10000;
let reconnectTimeout;
let alertDiv;


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
            alertDiv.remove();
        } catch {}
        console.log("Websocket connected");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("New message received:", data);
        switch (data.type) {
            case "new-image":
                transferImages();
                document.getElementById("img-0-span").hidden = true;
                img = document.getElementById("img-0-img");
                img.src = data.image_url;
                img.hidden = false;
                writeImageInfo(
                    data.origin,
                    "img-0-origin",
                    data.insp_result,
                    "img-0-type",
                    (data.trust * 100).toFixed(2) + '%',
                    "img-0-trust"
                )
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
        alertDiv.remove();
    } catch (error) {}
    alertDiv = document.createElement("div");
    alertDiv.className = `d-inline-block position-absolute top-2 end-0 alert alert-${type}`;
    alertDiv.textContent = message;
    document.getElementById("main-content").appendChild(alertDiv);
}

function clearImages() {
    for (let i = 4; i > 0; i--) {
        img = document.getElementById(`img-${i}-img`);
        img.src = "";
        img.hidden = true;
        document.getElementById(`img-${i}-span`).hidden = false;
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
        } catch (error) {}
    }
}

function transferImage(idOrigin, idDestiny) {
    imgDestiny = document.getElementById(`img-${idDestiny}-img`)
    spanDestiny = document.getElementById(`img-${idDestiny}-span`)
    imgOrigin = document.getElementById(`img-${idOrigin}-img`)
    spanOrigin = document.getElementById(`img-${idOrigin}-span`)
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
    trustElementName
) {
    document.getElementById(originElementName).innerText = origin
    document.getElementById(typeElementName).innerText = type
    document.getElementById(trustElementName).innerText = trust
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

initWebSocket();
