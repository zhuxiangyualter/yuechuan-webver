$(function () {
    $('#button-submit').click(submit);
});

async function listener(id) {
    const url = $('#status-url').val().replace('0', '');

    while (true) {
        const response = await fetch(url + id.toString());

        if (!response.ok) {
            continue;
        }

        const data = await response.json();

        if (data.complete === true) {
            return data;
        }

        await new Promise(resolve => setTimeout(resolve, 3000));
    }
}

function submit() {
    description = $('#description').val();
    if (description.trim().length == 0) {
        return;
    }
    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data: {
            'description': description,
        },
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        beforeSend: () => {
            $('.dimmer').addClass('active');
            $('#loader-input').text('正在处理');
            $('#skeleton').css('display', '');
        },
        success: data => {
            $('#loader-input').text('任务创建成功，正在生成');
            $('#skeleton').css('display', 'none');
            $('#preview').css('display', '');
            $('#preview-cover').attr('src', data.cover);
            $('#preview-title').text(data.title);
            $('#preview-subtitle').text(data.subtitle);
            $('#generation-id').val(data.id);
            
            listener(data.id).then(({ url }) => {
                $('.dimmer').removeClass('active');
                $('#button-download').click(() => {
                    window.open(`${window.location.protocol}//${window.location.host}${url}`);
                }).css('display', '');
                $('#description').val('');
            });
        },
    })
}