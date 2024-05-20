$(function () {
    recommend();
    $('#button-submit').click(() => ask());
    $('#button-refresh').click(() => recommend());
});

const message_history = [];

const wrap = (message) => {
    return $(`
        <div class="event">
            <div class="label">
                <img src="${$('#input-avatar').val()}">
            </div>
            <div class="content">
                <div class="summary">
                    <b class="user">${$('#input-username').val()}</b>: ${message}
                </div>
                <div class="extra text">...</div>
            </div>
        </div>
    `);
}

const left_aligned = (message) => {
    return wrap(message).wrap('<div class="ui left aligned container" />').parent();
}

const right_aligned = (message) => {
    return wrap(message).wrap('<div class="ui right aligned container" />').parent();
}

function ask() {
    const query = $('#question').val();
    $('#question').val('');
    if (query.trim().length == 0) {
        return;
    }

    const q = wrap(query).appendTo('.answer-container');

    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data: {
            query: query,
            type: 'ask',
            history: JSON.stringify(message_history),
            template: 'question'
        },
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        beforeSend: () => {
            $('.dimmer').addClass('active');
            message_history.push({
                role: 'user',
                content: query
            });
        },
        success: data => {
            q.find('.extra.text').text(data.content);
            message_history.push({
                role: 'assistant',
                content: data.content
            });
        },
    }).always(() => {
        $('.dimmer').removeClass('active');
    });
}
function recommend() {
    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data: {
            query: '-1',
            type: 'refresh',
        },
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        beforeSend: () => {
            $('.placeholder').css('display', '');
            $('.rec-ui').css('display', 'none');
            $('#button-refresh').addClass('loading');
        },
        success: data => {
            $('.placeholder').css('display', 'none');
            $('.rec-ui').css('display', '');
            cnt = 1
            data.recommendQ.forEach(re => {
                $(`#rc${cnt}`).val(re)
                $(`#ask${cnt}`).off('click')
                $(`#ask${cnt}`).click(function() {
                    $('#question').val(re)
                    ask();
                })
                cnt++;
            });
            $('#button-refresh').removeClass('loading');
        },
    });
}