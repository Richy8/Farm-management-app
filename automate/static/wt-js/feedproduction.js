$(document).ready(function () {

    // Handle Production Submit Click
    $('.productionForm').on('submit', function () {
        console.log('submitted');
        if ($('.productionForm input') == " ") {
            // console.log();
        } else {
            $('.productionForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Submitting, Please Wait..');
        }
    })

    // Handle update production submit click
    $('#updateProductionForm').on('submit', function () {
        if ($('#updateProductionForm input') == " ") {
            // console.log();
        } else {
            $('#updateProduction #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');
        }
    })

})