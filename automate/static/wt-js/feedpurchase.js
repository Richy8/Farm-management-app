$(document).ready(function () {
    $(document).on('click', '.edit', function (e) {
        let id = $(this).attr('id');

        $.ajax({
            type: 'POST',
            url: '/getid',
            data: id,
            dataType: 'json',
            success: function (data) {

                $('#vendorId').val(data.item_info[0]['id']);

                $('#vendorDate').val(data.item_info[0]['date']);

                $('#vendorName').val(data.item_info[0]['vendor']);

                let output = '';
                output += '<option value="' + data.item_info[0]['item'] + '">' + data.item_info[0]['item'] + '</option>';

                $('#vendorItem').html(output)

                $('#vendorQty').val(data.item_info[0]['v_qty']);

                $('#vendorPrice').val(data.item_info[0]['v_price']);

                // console.log(data.item_info)
            }
        })
        // console.log(id, 'clicked');
    })
})