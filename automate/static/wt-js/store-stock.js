$(document).ready(function () {

    // Handle New Purchase Button Click
    $('.newOutflow').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Submitting, Please Wait..');
        }
    });

    // Handle Purchase Update Button Click
    $('.updateOutflow').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            // $(this).find('#submitButton').text('Renaming, please wait...');
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');

        }
    });


    // Handle update Outflow form population
    $(document).on('click', '.editOutflow', function(){

        let id = $(this).attr('id');
        console.log('clicked', id)

        // Send Ajax Request
        $.ajax({

            url:'/feed_outflow',
            method:'POST',
            data: id,
            dataType:'json',
            success: function(data){

                let feed = data.outflow_info[0];
                
                $('#outflowRowId').val(feed.id);
                $('#updateOutflowQty').val(feed.qty)
                $('#updateOutflowDept').val(feed.dept)


            }

        })

    })


})