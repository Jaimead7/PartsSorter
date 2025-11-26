async function showAlert(message, type, seconds) {
    const alertBlock = document.createElement("div");
    alertBlock.className = `alert alert-${type} fade show position-absolute m-1 start-50 translate-middle-x text-truncate`;
    alertBlock.style.cssText = 'top:4rem; z-index: 9999;';
    alertBlock.textContent = message;
    document.getElementById("main-content").appendChild(alertBlock);
    setTimeout(() => {
        if (alertBlock?.parentNode) {
            alertBlock.remove();
        }
    }, seconds * 1000);
}


export { showAlert };
