$(document).ready(function(){

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

   // Spinner Icon On Click
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

   // Switch between Egg Producing Bird and Meat Producing Bird
   $('#panelOne').addClass('base-border');
    $('#panelTwo').addClass('base-borderless');
    $('.panel-two').hide();


    $('#panelOne').on('click', function(){
        $('#panelOne').removeClass('base-borderless');
        $('#panelOne').addClass('base-border');
        $('#panelTwo').removeClass('base-border');
        $('#panelTwo').addClass('base-borderless');
        $('.panel-one').show();
        $('.panel-two').hide();
    })

    $('#panelTwo').on('click', function(){
        $('#panelTwo').removeClass('base-borderless');
        $('#panelTwo').addClass('base-border');
        $('#panelOne').removeClass('base-border');
        $('#panelOne').addClass('base-borderless');
        $('.panel-one').hide();
        $('.panel-two').show();
    })


})