$ (document).ready (function () {
  $.ajax ({
    url: '/overview_chart',
    method: 'GET',
    success: function (data) {
      // console.table(data.items)

      let feeditems = [];
      let quantity = [];

      for (let item of data.items) {
        feeditems.push (item.item);
        quantity.push (item.c_qty);
      }
      // console.log(quantity)
      // Create a chartdata
      let chartData = {
        labels: feeditems,
        datasets: [
          {
            label: 'Stock',
            data: quantity,
            backgroundColor: 'cyan',
            pointBorderColor: 'maroon',
            pointBackgroundColor: 'aqua',
            lineTension: 0.5,
          },
        ],
      };

      // Create a new chart object
      let ctx = $ ('#myCanvas');

      let graph = new Chart (ctx, {
        type: 'line',
        data: chartData,
        options: {
          title: {
            display: true,
            text: 'Current Feed Item Stocks',
            fontColor: 'teal',
            fontSize: 14,
            position: 'bottom',
          },
          legend: {
            display: false,
          },
        },
      });
    },
    error: function (data) {
      console.log (data);
    },
  });
});
