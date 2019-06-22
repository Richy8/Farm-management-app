$(document).ready(function () {

    // Chart line graph(Ajax)
    $(document).on('click', '.type-button', function () {

        let id = $(this).attr('id')

        // console.log(id)
        $.ajax({

            method: 'POST',
            url: '/feedtype_id',
            data: id,
            dataType: 'json',
            success: function (data) {
                // console.table(data.feedlist)

                let feeditems = []
                let formula = []
                let feedtype = []

                for (let item of data.feedlist) {

                    feeditems.push(item.item);
                    formula.push(item.formula);
                    feedtype.push(item.type);

                }
                // console.log(feedtype)

                let chartData = {
                    labels: feeditems,
                    datasets: [{
                        label: 'Formulation',
                        data: formula,
                        backgroundColor: '#f37736',
                        pointBorderColor: 'maroon',
                        pointBackgroundColor: 'aqua'
                    }]
                }

                let ctx = $('#myCanvas')

                let graph = new Chart(ctx, {

                    type: 'line',
                    data: chartData,
                    options: {
                        title: {
                            display: true,
                            text: 'Current Formulation of ' + feedtype[0],
                            fontColor: 'teal',
                            fontSize: 14,
                            position: 'bottom'
                        },
                        legend: {
                            display: false
                        }
                    }

                })

            }

        })

    })

    // Update form population ajax
    $(document).on('click', '.edit-formulation', function () {

        let type_id = $(this).attr('id');

        // Needed to use these variables as global
        let feedid = []
        let feedtype = []
        let items = []
        let formula = []

        // console.log(type_id);
        $.ajax({

            method: 'POST',
            url: '/feedtype_form',
            data: type_id,
            dataType: 'json',
            success: function (data) {

                // console.table(data.feedtypes)

                for (let feed of data.feedtypes) {

                    feedid.push(feed.id);
                    feedtype.push(feed.type);
                    items.push(feed.item);
                    formula.push(feed.formula);

                }
                $('#feedId').val(feedid[0]);

                $('#feedType').val(feedtype[0]);

                for (let i = 0; i < formula.length; i++) {

                    $('#' + items[i]).val(formula[i]);

                }

                // Get Total Formulation
                let sum = 0;
                $.each(formula, function (i, val) {
                    sum = sum + val
                })

                $('#totalForm').text(sum);

            }

        })


        let input = $('#allInputs input');

        let inputsum = [];

        $(input).on('keyup', function () {

            for (let x = 0; x < formula.length; x++) {

                inputsum.push($('#' + items[x]).val());

            }

            // Selects number of items required from the array
            last_item = inputsum.slice(inputsum.length - items.length)
            // console.log(last_item);

            // Get Total Formulation
            let sums = 0;
            $.each(last_item, function (i, vals) {
                sums = sums + parseFloat(vals)
            })

            $('#totalForm').text(sums);

        })

    })


    $(document).on('click', '#newFeedButton', function () {

        // let zero = $('#inputFormula input').val(0);
        let type_id = "1";

        let allitems = document.querySelectorAll('#inputFormula')
        let itemsarray = []
        let feeditems = []

        $.ajax({

            method: 'POST',
            url: '/feedtype_form',
            data: type_id,
            dataType: 'json',
            success: function (data) {

                for (let new_item of data.feedtypes) {
                    feeditems.push(new_item.item)
                }
                // console.log(feeditems)

            }

        })

        $('#inputFormula input').on('keyup', function () {

            // console.log('input entered')
            for (let f = 0; f < allitems.length; f++) {

                itemsarray.push($('#f-' + feeditems[f]).val());

            }

            // console.log(itemsarray);
            last_items = itemsarray.slice(itemsarray.length - allitems.length)
            // console.log(last_items);

            // Get Total Formulation
            let new_sum = 0;
            $.each(last_items, function (i, num) {
                new_sum = new_sum + parseFloat(num)
            })

            $('#totalFormula').text(new_sum);

        })

    })



})