$(document).ready(function(){

   // Calculate Total Purchase Cost
   let total_cost = 0;
   $('#nextButton').on('click', function(){
      
       total_cost = (
           ($('#POCQty').val() * $('#POCCost').val()) +
           ($('#POLQty').val() * $('#POLCost').val()) +
           ($('#Spent_LayerQty').val() * $('#Spent_LayerCost').val()) +
           ($('#BroilerQty').val() * $('#BroilerCost').val()) +
           ($('#NoilerQty').val() * $('#NoilerCost').val())  +
           ($('#CockerelQty').val() * $('#CockerelCost').val())
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