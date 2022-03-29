// Turn the given canvas into a degree of change chart populated with the given data.
function degreeOfChangeChart(canvas, data) {
    // Create a chart that shows the degree of change over time.
    let ctx = canvas.getContext("2d");

    return new Chart(ctx, {
        type: "line",
        data: {
            datasets: [
                {
                    label: "Degree of change",
                    backgroundColor: "#79AEC8",
                    borderColor: "#417690",
                    data: data,
                    pointRadius: 4
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: "time",
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 12,
                        maxRotation: 0,
                    }
                },
            },
            plugins: {
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: "xy",
                    },
                    pan: {
                        enabled: true,
                        mode: 'xy',
                    },
                }
            }
        }
    });
}
