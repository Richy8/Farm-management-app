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

  // Handle New Vendor Button Click
  $('.newVendor').on('submit', function () {
    // console.log('Clicked');
    if ($(this).find('input') == ' ') {
      console.log();
    } else {
      $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
    }
  });

  // Handle Vendor Rename Button Click
  $('.renameVendorForm').on('submit', function () {
    // console.log('Clicked');
    if ($(this).find('input') == ' ') {
      console.log();
    } else {
      // $(this).find('#submitButton').text('Renaming, please wait...');
      $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Renaming, Please Wait..');

    }
  });


  // Handle New FarmItem Button Click
  $('.newItemForm').on('submit', function () {
    // console.log('Clicked');
    if ($(this).find('input') == ' ') {
      console.log();
    } else {
      $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
    }
  });

  // Handle FarmItem Rename Button Click
  $('.renameFarmItemForm').on('submit', function () {
    // console.log('Clicked');
    if ($(this).find('input') == ' ') {
      console.log();
    } else {
      // $(this).find('#submitButton').text('Renaming, please wait...');
      $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Renaming, Please Wait..');

    }
  });


  // Handle Vendor Rename form population
  $(document).on('click', '.renameVendor', function(){

    let id = $(this).attr('id');
    // console.log('clicked', id);

    // Send Ajax request
    $.ajax({

      url: '/rename_vendor',
      method: 'POST',
      data: id,
      dataType: 'json',
      success: function(data){

        let vendor = data.vendor_data[0];

        $('#vendorId').val(vendor.id);
        $('#vendorInput').val(vendor.vendor);

      },
      error: function(data){
        console.log(data);
      }


    })

  })


  // Handle Farm Item Rename form population
  $(document).on('click', '.renameFarmItem', function(){

    let id = $(this).attr('id');
    console.log('clicked', id);

    // Send Ajax request
    $.ajax({

      url: '/rename_farmitem',
      method: 'POST',
      data: id,
      dataType: 'json',
      success: function(data){

        let farmitem = data.farmitem_data[0];

        $('#farmitemId').val(farmitem.id);
        $('#farmitemInput').val(farmitem.farmitem);

      },
      error: function(data){
        console.log(data);
      }


    })

  })


  // Handle vendor delete id population
  $(document).on('click', '.deleteVendor', function(){

    let id = $(this).attr('id');
    // console.log('vendor', id);

    $('#vendorDeleteId').val(id)

  })


   // Handle farmitem delete id population
   $(document).on('click', '.deleteFarmItem', function(){

    let id = $(this).attr('id');
    // console.log('farmitem', id);

    $('#farmitemDeleteId').val(id);

  })

});