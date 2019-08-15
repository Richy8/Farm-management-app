$(document).ready(function () {

     // Handle New Customer Button Click
     $('.newCustomer').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Adding, Please Wait..');
        }
    });


    // Handle Customer Update Button Click
    $('.editCustomer').on('submit', function () {
        // console.log('Clicked');
        if ($(this).find('input') == ' ') {
            console.log();
        } else {
            // $(this).find('#submitButton').text('Renaming, please wait...');
            $(this).find('#submitButton').html('<div class="spinner-border spinner-border-sm"></div> Updating, Please Wait..');

        }
    });

    // Toggle NEXT and PREV bUUTTON
    $('.second-page').addClass('d-none');

    // Next Button Click
    $('.next-button').on('click', function(e){
        // Prevent Default beahaviour of form
        e.preventDefault();
        $('.first-page').addClass('d-none');
        $('.second-page').removeClass('d-none');
    })

    // Prev Button Click
    $('.prev-button').on('click', function(e){
         // Prevent Default beahaviour of form
        e.preventDefault();
        $('.first-page').removeClass('d-none');
        $('.second-page').addClass('d-none');
    })

    // Regions in Nigeria
    let northcentral = ['Benue', 'Kogi', 'Kwara', 'Nasarawa', 'Niger', 'Plateau', 'FCT'];
    let northeast = ['Adamawa', 'Bauchi', 'Borno', 'Gombe', 'Taraba', 'Yobe'];
    let northwest = ['Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Sokoto', 'Zamfara'];
    let southeast = ['Abia', 'Anambra', 'Ebonyi', 'Enugu', 'Imo',];
    let southsouth = ['Akwa-Ibom', 'Bayelsa', 'Cross River', 'Rivers', 'Delta', 'Edo'];
    let southwest = ['Ekiti', 'Lagos', 'Ogun', 'Ondo', 'Osun', 'Oyo'];

    $('#customerState').on('change', function(){
        let state = $(this).val();
        
        if (northcentral.includes(state)) {
            $('#customerRegion').val('North Central');
        }else if (northeast.includes(state)) {
            $('#customerRegion').val('North East');
        }else if (northwest.includes(state)) {
            $('#customerRegion').val('North West');
        }else if (southeast.includes(state)) {
            $('#customerRegion').val('South East');
        }else if (southsouth.includes(state)) {
            $('#customerRegion').val('South South');
        }else if (southwest.includes(state)) {
            $('#customerRegion').val('South West');
        }else {
            $('#customerRegion').val('Region not available');
        }

    })

    // Handle customer rename form population
    $(document).on('click', '.editButton', function(){

        let id = $(this).attr('id');
        // console.log("Clicked", id);

        $.ajax({

            url:'/edit_customer',
            method:'POST',
            data:id,
            dataType:'json',
            success: function(data){

                let customer = data.customer_info[0];

                $('#c_id').val(customer.id);
                $('#c_name').val(customer.name);
                $('#c_address').val(customer.address);
                $('#c_email').val(customer.email);
                $('#c_phone').val(customer.phone);
                $('#c_gender').val(customer.gender);
                $('#c_type').val(customer.type);
                $('#c_city').val(customer.city);
                $('.c_state').val(customer.state);
                $('.c_region').val(customer.region);


                $('#updateCustomerState').on('change', function(){
                    let state = $(this).val();
                    
                    if (northcentral.includes(state)) {
                        $('#updateCustomerRegion').val('North Central');
                    }else if (northeast.includes(state)) {
                        $('#updateCustomerRegion').val('North East');
                    }else if (northwest.includes(state)) {
                        $('#updateCustomerRegion').val('North West');
                    }else if (southeast.includes(state)) {
                        $('#updateCustomerRegion').val('South East');
                    }else if (southsouth.includes(state)) {
                        $('#updateCustomerRegion').val('South South');
                    }else if (southwest.includes(state)) {
                        $('#updateCustomerRegion').val('South West');
                    }else {
                        $('#updateCustomerRegion').val('Region not available');
                    }
            
                })

            }


        })
        
    })


    // Handle Customer delete form population
    $(document).on('click', '.deleteButton', function(){

        let id = $(this).attr('id');
        // console.log('clicked', id);

        $('#customerDeleteId').val(id);

    })


})