
// Language Page
function selectLanguage(selectedItem) {
    const items = document.querySelectorAll('.language-item');
    items.forEach(item => {
        item.classList.remove('selected');
    });
    selectedItem.classList.add('selected');
}
