document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("menu-button");
    const sidebar = document.getElementById("sidebar");

    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("sidebar-collapsed");
    });
});

function collapsSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (window.innerWidth < 650) {
        sidebar.classList.add("sidebar-collapsed")
    }
}

window.addEventListener("load", collapsSidebar);
window.addEventListener("resize", collapsSidebar);