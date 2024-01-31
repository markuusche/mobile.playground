function toast_check(text) {
    let digitalElement = document.querySelector('div#bet-msg-toast div');
    let confirmButton = document.querySelector('div.flex.Confirm');
    if (digitalElement) {
        if (digitalElement.textContent.trim() === text) {
            confirmButton.click();
            return true;
        }
    }
    return false;
}

function isFullScreen() {
    return (
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
    );
}

function preventFullScreen() {
    if (isFullScreen()) {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

function noFullScreen(){
    document.addEventListener('fullscreenchange', preventFullScreen);
    document.addEventListener('webkitfullscreenchange', preventFullScreen);
    document.addEventListener('mozfullscreenchange', preventFullScreen);
    document.addEventListener('MSFullscreenChange', preventFullScreen);
}

function scrollToTop(){
    window.scrollTo(0, 0);
}
