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
                document.getElementById("live-img-span").hidden = true;
                img = document.getElementById("live-img");
                img.src = data.image_url;
                img.hidden = false;
                writeImageInfo(
                    data.origin,
                    "live-img-origin",
                    data.insp_result,
                    "live-img-type",
                    (data.trust * 100).toFixed(2) + '%',
                    "live-img-trust"
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
    alertDiv.id = "alert-msg";
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    document.getElementById("main-content").appendChild(alertDiv);
}

function clearImages() {
    for (let i = 4; i > 1; i--) {
        img = document.getElementById(`hist-img-${i}`);
        img.src = "";
        img.hidden = true;
        document.getElementById(`hist-img-${i}-span`).hidden = false;
        clearImageInfo(`img-hist-origin-${i}`, `img-hist-type-${i}`, `img-hist-trust-${i}`)
    }
    img = document.getElementById("live-img");
    img.src = "";
    img.hidden = true;
    document.getElementById("live-img-span").hidden = false;
    clearImageInfo("live-img-origin", "live-img-type", "live-img-trust")
}

function transferImages() {
    for (let i = 4; i > 1; i--) {
        transferImage(`hist-img-${i-1}`, `hist-img-${i}`);
        transferText(`img-hist-origin-${i-1}`, `img-hist-origin-${i}`);
        transferText(`img-hist-type-${i-1}`, `img-hist-type-${i}`);
        transferText(`img-hist-trust-${i-1}`, `img-hist-trust-${i}`);
    }
    transferImage("live-img", "hist-img-1");
    transferText("live-img-origin", "img-hist-origin-1");
    transferText("live-img-type", "img-hist-type-1");
    transferText("live-img-trust", "img-hist-trust-1");
}

function transferImage(idOrigin, idDestiny) {
    imgDestiny = document.getElementById(idDestiny)
    imgOrigin = document.getElementById(idOrigin)
    imgDestiny.src = imgOrigin.src;
    imgDestiny.hidden = imgOrigin.hidden;
    document.getElementById(`${idDestiny}-span`).hidden = document.getElementById(`${idOrigin}-span`).hidden;
}

function transferText(idOrigin, idDestiny) {
    document.getElementById(idDestiny).textContent = document.getElementById(idOrigin).textContent;
}

function writeImageInfo(origin, originElementName, type, typeElementName, trust, trustElementName) {
    document.getElementById(originElementName).innerText = origin
    document.getElementById(typeElementName).innerText = type
    document.getElementById(trustElementName).innerText = trust
}

function clearImageInfo(originElementName, typeElementName) {
    const originElement = document.getElementById(originElementName);
    if (originElement) {
        originElement.innerText = originElement.getAttribute("data-default-text")
    }
    const typeElement = document.getElementById(typeElementName);
    if (typeElement) {
        typeElement.innerText = typeElement.getAttribute("data-default-text")
    }
    const trustElement = document.getElementById(trustElementName);
    if (trustElement) {
        trustElement.innerText = typeEtrustElementlement.getAttribute("data-default-text")
    }
}

initWebSocket();
