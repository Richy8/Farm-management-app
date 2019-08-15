$(document).ready(function(){

    // NUMBER FORMATTING
    function toCommas(value){
        return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }


    // HAndle dropDown Id on Click
    $(document).on('click', '#dropBox', function(){
        $('#dropBox i').toggleClass('fa-caret-up');
        $('#dropBox i').toggleClass('fa-caret-down');

        $('.dropbox-panel').toggleClass('d-none');
    })

    // Get Total Purchase Cost
    let total_cost;
    $(document).on('click', '.next-button', function(){
        total_cost = (
            ($('#PulletQty').val() * $('#PulletCost').val()) + 
            ($('#SmallQty').val() * $('#SmallCost').val()) +
            ($('#MediumQty').val() * $('#MediumCost').val()) +
            ($('#BigQty').val() * $('#BigCost').val()) +
            ($('#AdultQty').val() * $('#AdultCost').val()) +
            ($('#BEIJQty').val() * $('#BEIJCost').val())
        );
        // console.log(total_cost);
        $('.total-purchase').text(toCommas(total_cost));
    })


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


    // Hide Payment Details on load
   $('.payment-details').addClass('d-none');

//    On click of next button show payment details and hide cost details
   $('#nextButton').on('click', function(e){

        $('.cost-details').addClass('d-none');
        $('.payment-details').removeClass('d-none');

        e.preventDefault();

   })

   $('#prevButton').on('click', function(e){

        $('.payment-details').addClass('d-none');
        $('.cost-details').removeClass('d-none');

        e.preventDefault();

    })

    // Handle new sales form submission
    $('.newSales').on('submit', function(){
       
        if ($('.newSales input') == ' ') {
            console.log();
        } else {
            $('.newSales #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Submitting...');
           
        }

    })

    // Handle update remark form
    $('.remarkForm').on('submit', function(){

        if ($('.remarkForm textarea') == ' ') {
            console.log();
        } else {
            $('.remarkForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating...');
           
        }

    })

     // Handle update Cost Info form
     $('.costForm').on('submit', function(){

        if ($('.costForm input') == ' ') {
            console.log();
        } else {
            $('.costForm #submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating...');
           
        }

    })


    // Set Colors to Debit and Credit Balance
    $('.debit-present').parent('tr').addClass('red lighten-4');
    $('.credit-present').parent('tr').addClass('green lighten-4');

})