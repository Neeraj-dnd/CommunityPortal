console.log('Javascript: welcome to website');

document.addEventListener('DOMContentLoaded', function() {
    let menuButtons = document.getElementsByClassName('menu_button');
    let dropdownMenus = document.getElementsByClassName('dropdown_menu');

    if (menuButtons.length === 0 || dropdownMenus.length === 0) {
        // Ensure that elements are found
        return;
    }

    for (let i = 0; i < menuButtons.length; i++) {
        menuButtons[i].addEventListener('click', function(event) {
            console.log('clicked');
            let menuButton = menuButtons[i];
            let dropdownMenu = dropdownMenus[i];

            // Check if dropdownMenu is not null before accessing classList
            if (dropdownMenu) {
                menuButton.classList.toggle('active');
                // Reset the active state after a delay (adjust the delay as needed)
                setTimeout(() => {
                    menuButton.classList.remove('active');
                }, 300); // 300 milliseconds delay (0.3 seconds)
                dropdownMenu.classList.toggle('visible');
            }

            // Prevent the click event from propagating to the document click event
            event.stopPropagation();
        });
    }

    // Close the dropdown menu if the user clicks outside of it
    document.addEventListener('click', function() {
        console.log('clicked outside..');
        for (let i = 0; i < dropdownMenus.length; i++) {
            dropdownMenus[i].classList.remove('visible');
            menuButtons[i].classList.remove('active');
        }
    });
});
