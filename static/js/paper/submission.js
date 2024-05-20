$(function (){
    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data: {
            type: 'analysis',
        },
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        success: data => {
            $('#analysis-ui').css('display', '')
            $('#skeleton').css('display', 'none');
            $('#analysis').val(data.analysis)
        }
    });
})