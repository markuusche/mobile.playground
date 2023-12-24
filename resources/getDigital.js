function getDigital() {
    let digitalElement = document.querySelector('div#bet-msg-toast div');
    if (digitalElement) {
        if (digitalElement.textContent.trim() === 'Insufficient Balance') {
            return true;
        }
    }
    return false;
}
return getDigital();