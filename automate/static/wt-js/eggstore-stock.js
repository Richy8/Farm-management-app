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

    // Handle New Pen Button Click
    $('.newPen').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
        }
    });

    // Handle Pen rename Button Click
    $('.renamePen').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Renaming, Please Wait..');

        }
    });

    // Handle Stock update Button Click
    $('.addStock').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');

        }
    });

    // Handle Stock update Button Click
    $('.updateStock').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');

        }
    });

    // Handle Pen form rename
    $(document).on('click', '.renameButton', function(){

        let id  = $(this).attr('id');
        console.log('clicked', id);

        // Send Ajax request
        $.ajax({

            url:'/rename_pen',
            method:'POST',
            data: id,
            dataType:'json',
            success: function(data){

                let pen = data.pen_info[0];

                $('#penId').val(pen.id);
                $('#penOldName').val(pen.name);
                $('#penNewName').val(pen.name);

            }

        })

    })

    // Handle Delete of pen form
    $(document).on('click', '.deleteButton', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id)

        $('#penDeleteId').val(id)

    })


    // Handle update of eggstock form population
    $(document).on('click', '.editEggStock', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id);

        // Send Ajax request
        $.ajax({

            url: '/update_eggstock',
            method: 'POST',
            data: id,
            dataType: 'json',
            success: function(data){

                let stock = data.eggstock_info[0];

                $('#eggStockRowId').val(stock.id)
                $('#uProduction').val(stock.production)
                $('#uCracks').val(stock.cracks)

            }

        })

    })

});