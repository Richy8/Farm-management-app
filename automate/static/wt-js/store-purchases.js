$(document).ready(function () {

    // Handle New Purchase Button Click
    $('.newPurchase').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
        }
    });

    // Handle Purchase Update Button Click
    $('.updatePurchase').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            // $(this).find('#submitButton').text('Renaming, please wait...');
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');

        }
    });

    // Handle feeditem purchase update form
    $(document).on('click', '.editFeed', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id);

        // $('#updateFeedId').val(id);

        // Send ajax request
        $.ajax({

            url:'/update_feed',
            method:'POST',
            data: id,
            datatype:'json',
            success: function(data){

                // console.table(data.purchase_data)
                let feed = data.purchase_data[0];

                $('#updateFeedId').val(feed.id);
                $('#vendorName').val(feed.vendor)
                $('#feeditemName').val(feed.feeditem);
                $('#feedQty').val(feed.qty);
                $('#feedPrice').val(feed.price);


            }

        })

    })


    // Handle farmitem purchase update form
    $(document).on('click', '.editNonFeed', function(){

        let id = $(this).attr('id');
        console.log('clicked', id);

        // $('#updateFarmId').val(id);

         // Send ajax request
         $.ajax({

            url:'/update_nonfeed',
            method:'POST',
            data: id,
            datatype:'json',
            success: function(data){

                // console.table(data.purchase_data)
                let farmitem = data.purchase_nf[0];

                $('#updateFarmId').val(farmitem.id);
                $('#vendorName').val(farmitem.vendor)
                $('#farmitemName').val(farmitem.farmitem);
                $('#farmQty').val(farmitem.qty);
                $('#farmPrice').val(farmitem.price);


            }

        })

    })

})