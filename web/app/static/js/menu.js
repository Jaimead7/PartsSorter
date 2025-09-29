document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("toggle-sidebar");
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");

    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("sidebar-collapsed");
        mainContent.classList.toggle("main-content-expanded")
    });
});

function collapsSidebar() {
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");
    if (window.innerWidth < 650) {
        sidebar.classList.add("sidebar-collapsed")
        mainContent.classList.add("main-content-expanded")
    }
}

window.addEventListener("load", collapsSidebar);
window.addEventListener("resize", collapsSidebar);