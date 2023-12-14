function getDigital(){
    let digital = document.querySelector('div#bet-msg-toast div');
    let confirm = document.querySelector('div.flex.Confirm > div');
    if (digital.textContent == 'Insufficient Balance'){
        confirm.click();
    }
}
getDigital();