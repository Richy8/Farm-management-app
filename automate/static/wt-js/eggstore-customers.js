$(document).ready(function () {
    // Hide delete and rename icons on load
    $('.hiddenIcons i').hide();

    // Show on mouse over
    $('.hiddenIcons').on('mouseover', function () {
        $(this).find('i').show();
    });

    // Hide on mouse leave
    $('.hiddenIcons').on('mouseleave', function () {
        $(this).find('i').hide();
    });

    // Handle New Customer Button Click
    $('.newCustomer').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
        }
    });


    // Handle Customer Update Button Click
    $('.renameCustomer').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            // $(this).find('#submitButton').text('Renaming, please wait...');
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Renaming, Please Wait..');

        }
    });


    // Handle customer rename form population
    $(document).on('click', '.renameButton', function(){

        let id = $(this).attr('id');
        // console.log("Clicked", id);

        $.ajax({

            url:'/rename_customer',
            method:'POST',
            data:id,
            dataType:'json',
            success: function(data){

                let customer = data.customer_info[0];

                $('#nameId').val(customer.id)
                $('#oldName').val(customer.name)
                $('#newName').val(customer.name)

            }

        })

        
    })


    // Handle Customer delete form population
    $(document).on('click', '.deleteButton', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id);

        $('#customerDeleteId').val(id);

    })


});