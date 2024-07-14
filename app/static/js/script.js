$(document).ready(function () {
    var dataToProcess = ""
    $('#fileInputSection').hide();

    $('#inputType').change(function () {
        if ($(this).val() === 'text') {
            $('#fileInputSection').hide();
            $('#textInputSection').show();
        } else {
            $('#textInputSection').hide();
            $('#fileInputSection').show();
        }
    });

    $('#fileInput').change(function () {
        const fileInput = this;
        const reader = new FileReader();

        reader.onload = function (e) {
            dataToProcess = e.target.result;
            processPipeline();
        };

        reader.readAsText(fileInput.files[0]);
    });

    $('#submitText').click(function () {
        dataToProcess = $('#textInput').val();
        processPipeline();
    });

    $('#pipelineSelect').change(function () {
        processPipeline()
    });

    function createTable(headers, data) {
        var table = $('<table>');
        table.addClass("table")
        table.addClass("table-hover")

        if (headers.length != data.length) {
            console.log("Headers and data lengths do not match!")
            return table
        }

        for (let i = 0; i < data.length - 1; i++) {
            if (data[i].length != data[i + 1].length) {
                console.log("Data lengths are incosistent!")
                return table
            }
        }

        var thead = $('<thead>')
        thead.addClass('thead-light')
        table.append(thead)
        var headerRow = $('<tr>').appendTo(thead);
        headers.forEach(element => {
            const th = $('<th>').text(element);
            th.addClass('header');
            headerRow.append(th)
        });

        const tbody = $('<tbody>');

        const numRows = data[0].length;

        for (let i = 0; i < numRows; i++) {
            const row = $('<tr>');

            for (let j = 0; j < data.length; j++) {
                const cell = $('<td>')
                const pre = $('<pre>').text(data[j][i])
                if (j == 0) {
                    pre.addClass("pre-word-wrap")
                } else {
                    pre.addClass("pre-scroll")
                }
                cell.append(pre)
                row.append(cell)
            }

            tbody.append(row);
        }

        table.append(tbody);

        return table
    }

    function showPipeline(data) {
        const pipelineStage = $('#pipelineSelect').val();

        if (pipelineStage == "input") {
            $("#pipelineSelect").val("suggest");
            $("#userInput").show();
            return;
        }
        let headers = [];
        let tableData = [];
        switch (pipelineStage) {
            case "suggest":
                headers.unshift(data.suggest.header);
                tableData.unshift(data.suggest.output);
            case "extract":
                headers.unshift(data.extract.header);
                tableData.unshift(data.extract.output);
            case "preprocess":
                headers.unshift(data.preprocess.header);
                tableData.unshift(data.preprocess.output);
                break;
            default:
                console.log("Selected pipeline doesn't exist or it is under development.");
                return;
        }
        $("#userInput").hide();
        $("#table-container").empty()
        let table = createTable(headers, tableData)
        $("#table-container").append(table)
    }

    function processPipeline() {
        $("#table-container").empty()

        let text = dataToProcess;
        const pipelineStage = $('#pipelineSelect').val();

        if (text) {
            const body_text = JSON.stringify({ text, pipelineStage })

            fetch('/process', {
                method: 'POST',
                body: body_text,
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    $('#pipelineOutput').hide()
                    $('#inputOutput').hide()
                    showPipeline(data)
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    }
});
