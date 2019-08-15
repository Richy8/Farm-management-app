$(document).ready(function(){

  // Handle display of Crop Cost Settings
    $('.crop-section').hide();

    $('#allocationPineapple').on('click', function(){
        $('.pineapple-section').toggle();
        $('.crop-section').hide();
        $('#allocationPineapple i').toggleClass('fa-caret-up');
        $('#allocationPineapple i').toggleClass('fa-caret-down');
    });

    $('#allocationCrop').on('click', function(){
        $('.pineapple-section').hide();
        $('.crop-section').toggle();
        $('#allocationCrop i').toggleClass('fa-caret-up');
        $('#allocationCrop i').toggleClass('fa-caret-down');
    });


    // Calculate Total Purchase Cost
    let total_cost = 0;
    $('#nextButton').on('click', function(){
       
        total_cost = (
            ($('#CassavaQty').val() * $('#CassavaCost').val()) +
            ($('#PalmsQty').val() * $('#PalmsCost').val()) +
            ($('#UgwuQty').val() * $('#UgwuCost').val()) +
            ($('#TypeAQty').val() * $('#TypeACost').val()) +
            ($('#TypeBQty').val() * $('#TypeBCost').val())  +
            ($('#TypeCQty').val() * $('#TypeCCost').val()) +
            ($('#TypeDQty').val() * $('#TypeDCost').val()) +
            ($('#TypeEQty').val() * $('#TypeECost').val()) +
            ($('#TypeFQty').val() * $('#TypeFCost').val()) +
            ($('#SuckersQty').val() * $('#SuckersCost').val()) 
        );
        //  console.log(total_cost);
        $('.total-purchase').text(total_cost);
    })

    // Hide the Refund Section on load except outstannding balance is greater than one
    $('#refundSection').hide();

    let total_payment = 0;
    $('#bankPayment').on('keyup', function(){
        total_payment = (parseInt($('#bankPayment').val()) + parseInt($('#cashPayment').val()));

        // Compare total_payment to total_cost
        if (total_payment > total_cost) {
            let over = total_payment - total_cost;
            $('#refundSection').show();
            $('#outstandingBalance').val(over);
            $('#creditPurchase').val(0);

        }else if (total_cost > total_payment) {
            let under = total_cost - total_payment;
            $('#refundSection').hide();
            $('#creditPurchase').val(under);
            $('#outstandingBalance').val(0);

        }else {
            $('#outstandingBalance').val(0);
            $('#creditPurchase').val(0);
            $('#refundSection').hide();
        }

    })

    $('#cashPayment').on('keyup', function(){
        total_payment = (parseInt($('#bankPayment').val()) + parseInt($('#cashPayment').val()));

        // Compare total_payment to total_cost
        if (total_payment > total_cost) {
            let over = total_payment - total_cost;
            $('#refundSection').show();
            $('#outstandingBalance').val(over);
            $('#creditPurchase').val(0);

        }else if (total_cost > total_payment) {
            let under = total_cost - total_payment;
            $('#refundSection').hide();
            $('#creditPurchase').val(under);
            $('#outstandingBalance').val(0);

        }else {
            $('#outstandingBalance').val(0);
            $('#creditPurchase').val(0);
            $('#refundSection').hide();
        }

    })

})