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

    // Handle farmitem update outflow form population
    $(document).on('click', '.editOutflow', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id);

        // Send Ajax request
        $.ajax({

            url:'/farmitem_outflow_update',
            method:'POST',
            data:id,
            dataType: 'json',
            success: function(data){

                let item = data.farmitem_info[0];
                // console.table(data.farmitem_info);

                $('#nfRowId').val(item.id)
                $('#nfOutflowDept').val(item.dept)
                $('#nfOutflowQty').val(item.qty)

            }

        })

    })


})