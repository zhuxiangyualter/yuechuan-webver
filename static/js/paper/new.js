$('.ui.dropdown').dropdown();

$('input[name="tags"]').change(e => {
    search($(e.target).val().split(','));
});

const selected = [];

function search(tags) {
    if (tags.length == 0 || (tags.length == 1 && tags[0] == '')) {
        return;
    }
    $('.dimmer').addClass('active');
    $('.ui.dropdown').dropdown('hide');
    
    $('#search-results').empty();
    
    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data: {
            type: 'search',
            tags: JSON.stringify(tags),
        },
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        success: data => {
            $('.dimmer').removeClass('active');
            data.result.forEach(({ id, title, statement}) => {
                $(` <div class="item" data-pid=${id} data-title=${title} data-statement=${statement}>
                        <div class="right floated content">
                            <button class="ui button">添加</button>
                        </div>
                        <div class="content">
                            <h5>#${id} - ${title}</h5>
                            <p style="color: #000000; font-style: italic;">${statement}</p>
                        </div>
                    </div>`).appendTo('#search-results').find('button').click(addProblem);
            });
        }
    });
}

function refresh() {
    $('#selected-problems').empty();
    $('input[name="problems"]').val(JSON.stringify(selected.map(val => val.id)));
    selected.forEach(({ id, title, statement }) => {
        $(` <tr data-pid=${id}>
                <td >${id}</td>
                <td>${title}</td>
                <td>
                    <div class="ui input">
                        <input name="score${id}" type="number" value="10" style="width: 64px;">
                    </div>
                </td>
                <td>
                    <button class="ui button">删除</button>
                </td>
            </tr>`).appendTo('#selected-problems').find('button').click(removeProblem);
    })
}

function addProblem(event) {
    const q = $(event.target).parents('.item');
    if (selected.some(val => val.id == q.data('pid'))) return;
    selected.push({
        id: q.data('pid'),
        title: q.data('title'),
        statement: q.data('statement'),
    });
    refresh();
}

function removeProblem(event) {
    const q = $(event.target).parents('tr');
    selected.splice(selected.indexOf(q.data('pid')), 1);
    refresh();
}