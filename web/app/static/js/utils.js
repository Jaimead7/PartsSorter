let apiIP = null;

async function showAlert(message, type, seconds) {
    const alertBlock = document.createElement("div");
    alertBlock.className = `alert alert-${type} fade show position-absolute m-1`;
    alertBlock.style.cssText = 'top:4rem; z-index: 9999;';
    alertBlock.textContent = message;
    document.getElementById("main-content").appendChild(alertBlock);
    setTimeout(() => {
        if (alertBlock?.parentNode) {
            alertBlock.remove();
        }
    }, seconds * 1000);
}

async function getAPIIP() {
    if (apiIP === null) {
        try {
            const response = await fetch("/config/ip");
            const config = await response.json();
            apiIP = config.ip;
        } catch (error) {
            console.error("Error loading config:", error);
            throw new Error("Error loading config:", error)
        }
    }
    return apiIP;
}