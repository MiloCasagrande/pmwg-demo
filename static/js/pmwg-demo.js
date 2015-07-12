$(document).ready(function() {
    var chartProbe1;
    var dataSplitRegExp = new RegExp('[\n|\r|\n\r]', 'g');
    var lineSplitRegExp = new RegExp('\\s', 'g');
    var allCharts = [];

    function parseMessage(message) {
        var datum;
        datum = message.trim();
        datum = datum.split(lineSplitRegExp);
        return [
            new Date(parseFloat(datum[0], 10) * 1000),
            parseFloat(datum[1], 10)
        ];
    }

    function registerWebSockets() {
        var ws;
        allCharts.forEach(function(datum) {
            ws = new WebSocket(
                'ws://localhost:8888/websocket?probe=' + datum[1]);
            // TODO: handle close connection in a better way.
            window.onbeforeunload = function() {
                ws.close();
            };
            ws.onmessage = function(event) {
                var message = event.data.trim(),
                    series = datum[0].series[0],
                    seriesData = series.processedXData,
                    shift = false;
                if (message.length > 0) {
                    // TODO handle graph shift?
                    series.addPoint(parseMessage(message), true, shift);
                }
            };
        });
    }

    chartProbe1 = new Highcharts.Chart({
        chart: {
            type: 'spline',
            renderTo: 'chart-probe-1',
            panning: true
        },
        credits: {
            enabled: false
        },
        title: {
            text: 'Data read from sensor 1'
        },
        xAxis: {
            type: 'datetime',
            startOnTick: true
        },
        yAxis: {
            title: {
                text: 'Value'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        legend: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: [{
            name: 'Data read',
            data: []
        }]
    });
    allCharts.push([chartProbe1, 'probe1']);
    registerWebSockets();
});
