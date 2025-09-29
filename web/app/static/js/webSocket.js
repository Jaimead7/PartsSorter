const noImage = document.getElementById("no-live-image");
let ws;
let reconnectDelay = 10000;
let reconnectTimeout;
let alertDiv;

function connectWebSocket() {
    ws = new WebSocket("ws://localhost:8000/ws/image-stream"); //TODO: hide on finall deploy

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
                noImage.hidden = true;
                img = document.createElement("img");
                img.setAttribute("id", "live-image")
                img.setAttribute("class", "live-image")
                document.getElementById("live-image-image").appendChild(img);
                img.src = data.image_url;
                writeImageInfo(
                    data.origin,
                    "live-image-origin",
                    data.insp_result,
                    "live-image-type"
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
        connectWebSocket();
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
        const img = document.getElementById(`image-history-image-${i}`);
        img.src = ""
        clearImageInfo(`image-history-origin-${i}`, `image-history-type-${i}`)
    }
    const img = document.getElementById("live-image");
    if (img) {
        img.remove();
        clearImageInfo("live-image-origin", "live-image-type")
    }
    noImage.hidden = false;
}

function transferImages() {
    for (let i = 4; i > 1; i--) {
        transferImage(`image-history-image-${i-1}`, `image-history-image-${i}`);
        transferText(`image-history-origin-${i-1}`, `image-history-origin-${i}`);
        transferText(`image-history-type-${i-1}`, `image-history-type-${i}`);
    }
    transferImage("live-image", "image-history-image-1");
    transferText("live-image-origin", "image-history-origin-1");
    transferText("live-image-type", `image-history-type-1`);
    try {
        document.getElementById("live-image").remove()
    } catch (error) {}
}

function transferImage(idOrigin, idDestiny) {
    const origin = document.getElementById(idOrigin);
    const destiny = document.getElementById(idDestiny);
    if (origin && destiny) {
        destiny.src = origin.src;
    }
}

function transferText(idOrigin, idDestiny) {
    const origin = document.getElementById(idOrigin);
    const destiny = document.getElementById(idDestiny);
    if (origin && destiny) {
        destiny.textContent = origin.textContent;
    }
}

function writeImageInfo(origin, originElementName, type, typeElementName) {
    const originElement = document.getElementById(originElementName);
    if (originElement) {
        originElement.innerText = origin
    }
    const typeElement = document.getElementById(typeElementName);
    if (typeElement) {
        typeElement.innerText = type
    }
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
}

connectWebSocket();
