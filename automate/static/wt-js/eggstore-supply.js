$(document).ready(function () {

    // Handle New Purchase Button Click
    $('.newSupply').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Submitting, Please Wait..');
        }
    });

    // Handle Purchase Update Button Click
    $('.updateSupply').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            // $(this).find('#submitButton').text('Renaming, please wait...');
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');

        }
    });

})