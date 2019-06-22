$(document).ready(function () {

    // Handle Authorized Button Click
    $('.approveForm').on('submit', function(){

        $(this).find('#approveButton').html('<div class="spinner-border spinner-border-sm"></div>');

    })

     // Handle Decline Button Click
     $('.declineForm').on('submit', function(){

        $(this).find('#declineButton').html('<div class="spinner-border spinner-border-sm"></div>');

    })

})