$(document).ready(function(){

// Handle New User Button Click
$('.addUsers').on('submit', function () {
    // console.log('Clicked');
    if ($('.addUsers input') == ' ') {
        console.log();
    } else {
        $('.addUsers #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
    }
});


// Handle Update Users Button Click
$('.updateUsers').on('submit', function () {
    // console.log('Clicked');
    if ($('.updateUsers input') == ' ') {
        console.log();
    } else {
        $('.updateUsers #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');
    }
});


// Handle Delete Users Button Click
$('.deleteUsers').on('submit', function () {
    // console.log('Clicked');
    if ($('.deleteUsers input') == ' ') {
        console.log();
    } else {
        $('.deleteUsers #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Deleting, Please Wait..');
    }
});


// Handle User Id Update Role form population
$(document).on('click', '.editButton', function(){

    let id = $(this).attr('id');
    // console.log(id);

    // Send ajax request
    $.ajax({

        url: 'update_userrole',
        method: 'POST',
        data: id,
        datatype: 'json',
        success: function(data){

            let user = data.userData[0];

            $('#userId').val(user.id);
            $('#userEmail').val(user.email);

        }

    })

})


// Handle User Id Delete form population
$(document).on('click', '.deleteButton', function(){

    let id = $(this).attr('id');
    // console.log(id);

    // Send ajax request
    $.ajax({

        url: 'delete_user',
        method: 'POST',
        data: id,
        datatype: 'json',
        success: function(data){

            let user = data.user_data[0];

            $('#delete_user_id').val(user.id);
            $('#username').text(user.username);

        }

    })

})


})