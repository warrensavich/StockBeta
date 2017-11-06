var chart = undefined;

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function convert_date(inputformat) {
  function pad(s) { return (s < 10) ? '0' + s : s; }
  var d = new Date(inputformat);
  return [pad(d.getMonth()+1), pad(d.getDate()), d.getFullYear()].join('/');
}

function create_dataset(symbol, set) {
  var data = [];
  for (var date in set) {
    data.push({x: new Date( date.replace(/(\d{2})-(\d{2})-(\d{4})/, "$2/$1/$3") ), y: set[date]});
  }
  var set_color = getRandomColor();
  var dataset = {
    label: symbol,
    data: data,
    borderColor: set_color,
    backgroundColor: set_color
  }
  return dataset;
};

function tooltip_title_callback(element, datasets) {
  return datasets.datasets[element.datasetIndex].label + " Beta: " + element.yLabel +
    " Date: " + convert_date(element.xLabel);
};

function plot_data(data) {
  var datasets = [];
  for (var s in data) {
    datasets.push(create_dataset(s, data[s]))
  }
  var ctx = document.getElementById("graph_canvas").getContext("2d");
  if (chart) {
    chart.destroy();
  }
  chart = new Chart(ctx, {type: 'scatter',
                          data: {datasets: datasets},
                          responsive: false,
                          height: 400,
                          width: 900,
                          options: {
                            legend: {
                              display: false
                            },
                            tooltips: {
                              callbacks: {
                                label: tooltip_title_callback
                              }
                            },
                            scales: {
                              yAxes: [{
                                scaleLabel: {
                                  display: true,
                                  labelString: 'Beta'
                                }
                              }],
                              xAxes: [{
                                type: 'time',
                                time: {
                                  displayFormats: {
                                    quarter: 'MMM YYYY'
                                  }
                                }
                              }]
                            },
                            pan: {
                              enabled: true,
                              mode: 'xy'
                            },
                            zoom: {
                              enabled: true,
                              mode: 'xy'
                            }
                          }});
};

$("#beta_window_selection_form").submit(function(e) {
  e.preventDefault();
  $("#beta-new-data .glyphicon").addClass("glyphicon-spin");
  var start_date = $("#start_date").val();
  var end_date = $("#end_date").val();
  var url = '/api/v1/fetch-new-data?start_date=' + start_date + "&end_date=" + end_date;
  var ticker_id = $("#ticker_picker").val();
  if (ticker_id != "all") {
    url = url + "&symbol_id=" + ticker_id;
  }
  var comparator_id = $("#comparator_picker").val();
  if (comparator_id != "default") {
    url = url + "&comparator_id=" + comparator_id;
  }
  $.ajax({
      type: 'GET',
      url: url,
      success: function(data) {
        if (data.status === 'OK') {
          plot_data(data.data);
        }
        $("#beta-new-data .glyphicon").removeClass("glyphicon-spin");
      },
      error: function() {
        alert("An error occurred requesting new data");
        $("#beta-new-data .glyphicon").removeClass("glyphicon-spin");
      }
    });
});
