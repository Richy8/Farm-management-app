$(document).ready(function () {

    // Handle New Item Button Click
    $('#newItemForm').on('submit', function () {
        // console.log('Clicked');
        if ($('#newItemForm input') == ' ') {
            console.log();
        } else {
            $('#newItemForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
        }
    });

    // Handle Rename button Click
    $('#renameItemForm').on('submit', function () {
        // console.log('Clicked');
        if ($('#renameItemForm input') == ' ') {
            console.log();
        } else {
            $('#renameItemForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Renaming, Please Wait..');
        }
    });

    // Handle update button click
    $('#updateItemForm').on('submit', function () {
        // console.log('Clicked');
        if ($('#updateItemForm input') == ' ') {
            console.log();
        } else {
            $('#updateItemForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');
        }
    });

    // Handle Population of rename form
    $(document).on('click', '.rename-button', function () {
        let id = $(this).attr('id')
        // console.log(id, 'rename button clicked');

        $.ajax({
            method: 'POST',
            url: '/getitem_id',
            data: id,
            dataType: 'json',
            success: function (data) {

                let item = data.item[0];

                $('#nameId').val(item['id'])
                $('#oldName').val(item['item'])
                $('#newName').val(item['item'])
                // console.table(data.item)
            }
        })

    })

    // Handle Population of Update Form
    $(document).on('click', '.updatestock', function(){
        let id = $(this).attr('id');
        // console.log('update', id);

        $.ajax({
            method: 'POST',
            url: '/getstock_id',
            data: id,
            dataType: 'json',
            success: function (data) {

                let stock = data.stock[0];

                $('#itemQuantity').val(stock['o_qty']);
                $('#itemPrice').val(stock['o_price']);
                $('#updateId').val(id);
                console.table(data.stock)
            }
        })
    })

})