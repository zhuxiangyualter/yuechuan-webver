$('.ui.dropdown').dropdown();

$('input[name="tags"]').change(e => {
    search($(e.target).val().split(','));
});

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
        console.log(data.result)
        data.result.forEach(({ id, title, statement}) => {
            $(` <div class="item" data-pid=${id} data-title=${title} data-statement=${statement}>
                    <div class="content">
                        <h5><a href="${id}">#${id} - ${title}</a></h5>
                        <p style="color: #000000; font-style: italic;">${statement}</p>
                    </div>
                </div>`).appendTo('#search-results');
        });
    }
});
}