// Turn the given canvas into a usage chart populated with the given data.
function usageChart(canvas, usage_data, type) {
    let ctx = canvas.getContext("2d");

    var label = type === "api" ? "API Usage" : "Job Usage"
    var backgroundColor = type === "api" ? "#ffb1c1" : "#79AEC8"
    var borderColor = type === "api" ? "#ff6384" : "#417690"

    return new Chart(ctx, {
        type: "line",
        data: {
            labels: usage_data.labels,
            datasets: [
                {
                    label: label,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    data: usage_data.data,
                    pointRadius: 4
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    suggestedMin: 0,
                    ticks: {
                        callback: function (value) {
                            if (value % 1 === 0) {
                                return value
                            }
                        }
                    }
                },
            }
        }
    });
}
