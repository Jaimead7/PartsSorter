document.addEventListener('DOMContentLoaded', function() {
    // SET DATE
    document.getElementById('dateStartFilter').valueAsDate = new Date(new Date().setMonth(new Date().getMonth() - 1));
    document.getElementById('dateEndFilter').valueAsDate = new Date();

    // COLLAPSE
    const collapseElement = document.getElementById('dateFilterCollapseCard');
    const buttonIcon = document.querySelector('button[data-bs-target="#dateFilterCollapseCard"] .bi');
    
    collapseElement.addEventListener('show.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-down-square');
        buttonIcon.classList.add('bi-caret-up-square');
    });
    
    collapseElement.addEventListener('hide.bs.collapse', function() {
        buttonIcon.classList.remove('bi-caret-up-square');
        buttonIcon.classList.add('bi-caret-down-square');
    });
});