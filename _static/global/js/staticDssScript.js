let staticDSS_button = document.getElementById('staticDSS-button');
let dssContent_container = document.getElementById('dss-content-container');


staticDSS_button.addEventListener('click', function() {
    var dssContent = document.getElementById('dss-content');
    if (dssContent.style.display === 'none' || dssContent.style.display === '') {
        dssContent.style.display = 'block';
        dssContent_container.style.display = 'block';
        // Update the value of the dssButtonClicked input field
        submit_ButtonClicked();
    } else {
        dssContent.style.display = 'none';
        dssContent_container.style.display = 'none';
    }
});

function submit_ButtonClicked(){
    liveSend({'user_input': "clicked"});
}
