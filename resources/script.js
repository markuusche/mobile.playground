function toast_check(text) {
    let digitalElement = document.querySelectorAll('#toast-container .toast-item');
    if (digitalElement) {
        for (let element of digitalElement) {
            if (element.textContent.trim() === text) {
                return true;
            }
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

function noFullScreen() {
    document.addEventListener('fullscreenchange', preventFullScreen);
    document.addEventListener('webkitfullscreenchange', preventFullScreen);
    document.addEventListener('mozfullscreenchange', preventFullScreen);
    document.addEventListener('MSFullscreenChange', preventFullScreen);
}

function currVersion() {
    let version = document.querySelector('div.dev-version');
    return version.textContent;
}

//selenium click too slow with slow internet, improvising with JS clicks ;0
function click(locator){
    document.querySelector(locator).click();
}

//clicks a single element from the list
function selectGameList(selector, index){
    let game = document.querySelectorAll(`${selector}`);
        game[index].click();
    }

function sedieBeads(){
    var textStrings = ["ALL WHITE", "ONE RED", "ONE WHITE", "FOUR RED"];
    var locator = 'div.flex.beads-icon.xs8'
    document.querySelectorAll(`${locator}`).forEach(function(element, index) {
    Array.from(element.childNodes).forEach(function(childNode) {
        if (childNode.nodeName === 'DIV') {
            element.removeChild(childNode);
        }
    });

    var textNode = document.createTextNode(textStrings[index]);
    element.insertBefore(textNode, element.querySelector('span'));
});

    var elements = document.querySelectorAll(`div.setting-slot ${locator}`);
    elements.forEach(function(element) {
        element.className = element.className.replace('beads-icon', 'bet-label');
    });
}
