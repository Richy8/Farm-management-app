$(document).ready(function(){

     // Hide all Allocation Boxes
     $('.allocation-1').hide();
     $('.allocation-2').hide();
     $('.allocation-3').hide();
     $('.allocation-4').hide();
     $('.allocation-5').hide();
     $('.allocation-6').hide();
 
     // Show Allocation-box on click
     $('#allocation1').on('click', function(){
         $('#allocation1 i').toggleClass('fa-caret-up');
         $('#allocation1 i').toggleClass('fa-caret-down');
         
         $('#allocation2 i').addClass('fa-caret-up');
         $('#allocation2 i').removeClass('fa-caret-down');
 
         $('#allocation3 i').addClass('fa-caret-up');
         $('#allocation3 i').removeClass('fa-caret-down');
 
         $('#allocation4 i').addClass('fa-caret-up');
         $('#allocation4 i').removeClass('fa-caret-down');
 
         $('#allocation5 i').addClass('fa-caret-up');
         $('#allocation5 i').removeClass('fa-caret-down');
 
         $('#allocation6 i').addClass('fa-caret-up');
         $('#allocation6 i').removeClass('fa-caret-down');
 
         $('.allocation-1').toggle();
         $('.allocation-2').hide();
         $('.allocation-3').hide();
         $('.allocation-4').hide();
         $('.allocation-5').hide();
         $('.allocation-6').hide();
 
     })
 
     $('#allocation2').on('click', function(){
         $('#allocation2 i').toggleClass('fa-caret-up');
         $('#allocation2 i').toggleClass('fa-caret-down');
 
         $('#allocation1 i').addClass('fa-caret-up');
         $('#allocation1 i').removeClass('fa-caret-down');
 
         $('#allocation3 i').addClass('fa-caret-up');
         $('#allocation3 i').removeClass('fa-caret-down');
 
         $('#allocation4 i').addClass('fa-caret-up');
         $('#allocation4 i').removeClass('fa-caret-down');
 
         $('#allocation5 i').addClass('fa-caret-up');
         $('#allocation5 i').removeClass('fa-caret-down');
 
         $('#allocation6 i').addClass('fa-caret-up');
         $('#allocation6 i').removeClass('fa-caret-down');
 
         $('.allocation-1').hide();
         $('.allocation-2').toggle();
         $('.allocation-3').hide();
         $('.allocation-4').hide();
         $('.allocation-5').hide();
         $('.allocation-6').hide();
     })
 
     $('#allocation3').on('click', function(){
         $('#allocation3 i').toggleClass('fa-caret-up');
         $('#allocation3 i').toggleClass('fa-caret-down');
 
         $('#allocation1 i').addClass('fa-caret-up');
         $('#allocation1 i').removeClass('fa-caret-down');
 
         $('#allocation2 i').addClass('fa-caret-up');
         $('#allocation2 i').removeClass('fa-caret-down');
 
         $('#allocation4 i').addClass('fa-caret-up');
         $('#allocation4 i').removeClass('fa-caret-down');
 
         $('#allocation5 i').addClass('fa-caret-up');
         $('#allocation5 i').removeClass('fa-caret-down');
 
         $('#allocation6 i').addClass('fa-caret-up');
         $('#allocation6 i').removeClass('fa-caret-down');
 
         $('.allocation-1').hide();
         $('.allocation-2').hide();
         $('.allocation-3').toggle();
         $('.allocation-4').hide();
         $('.allocation-5').hide();
         $('.allocation-6').hide();
     })
 
     $('#allocation4').on('click', function(){
         $('#allocation4 i').toggleClass('fa-caret-up');
         $('#allocation4 i').toggleClass('fa-caret-down');
 
         $('#allocation1 i').addClass('fa-caret-up');
         $('#allocation1 i').removeClass('fa-caret-down');
 
         $('#allocation2 i').addClass('fa-caret-up');
         $('#allocation2 i').removeClass('fa-caret-down');
 
         $('#allocation3 i').addClass('fa-caret-up');
         $('#allocation3 i').removeClass('fa-caret-down');
 
         $('#allocation5 i').addClass('fa-caret-up');
         $('#allocation5 i').removeClass('fa-caret-down');
 
         $('#allocation6 i').addClass('fa-caret-up');
         $('#allocation6 i').removeClass('fa-caret-down');
 
 
         $('.allocation-1').hide();
         $('.allocation-2').hide();
         $('.allocation-3').hide();
         $('.allocation-4').toggle();
         $('.allocation-5').hide();
         $('.allocation-6').hide();
     })
 
     $('#allocation5').on('click', function(){
         $('#allocation5 i').toggleClass('fa-caret-up');
         $('#allocation5 i').toggleClass('fa-caret-down');
 
         $('#allocation1 i').addClass('fa-caret-up');
         $('#allocation1 i').removeClass('fa-caret-down');
 
         $('#allocation2 i').addClass('fa-caret-up');
         $('#allocation2 i').removeClass('fa-caret-down');
 
         $('#allocation3 i').addClass('fa-caret-up');
         $('#allocation3 i').removeClass('fa-caret-down');
 
         $('#allocation4 i').addClass('fa-caret-up');
         $('#allocation4 i').removeClass('fa-caret-down');
 
         $('#allocation6 i').addClass('fa-caret-up');
         $('#allocation6 i').removeClass('fa-caret-down');
 
 
         $('.allocation-1').hide();
         $('.allocation-2').hide();
         $('.allocation-3').hide();
         $('.allocation-4').hide();
         $('.allocation-5').toggle();
         $('.allocation-6').hide();
     })
 
     $('#allocation6').on('click', function(){
         $('#allocation6 i').toggleClass('fa-caret-up');
         $('#allocation6 i').toggleClass('fa-caret-down');
 
         $('#allocation1 i').addClass('fa-caret-up');
         $('#allocation1 i').removeClass('fa-caret-down');
 
         $('#allocation2 i').addClass('fa-caret-up');
         $('#allocation2 i').removeClass('fa-caret-down');
 
         $('#allocation3 i').addClass('fa-caret-up');
         $('#allocation3 i').removeClass('fa-caret-down');
 
         $('#allocation4 i').addClass('fa-caret-up');
         $('#allocation4 i').removeClass('fa-caret-down');
 
         $('#allocation5 i').addClass('fa-caret-up');
         $('#allocation5 i').removeClass('fa-caret-down');
 
 
         $('.allocation-1').hide();
         $('.allocation-2').hide();
         $('.allocation-3').hide();
         $('.allocation-4').hide();
         $('.allocation-5').hide();
         $('.allocation-6').toggle();
     })
 

})