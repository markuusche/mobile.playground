function toast_check() {
    let digitalElement = document.querySelector('div#bet-msg-toast div');
    if (digitalElement) {
        if (digitalElement.textContent.trim() === 'Insufficient Balance') {
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
