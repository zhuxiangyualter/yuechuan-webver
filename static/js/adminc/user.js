
$('.button-delete-user').click(deleteUser);
$('.button-ban-user').click(toggleBan);
$('.button-edit-user').click(showEditDialog);
$('.ui.icon.button').popup();
$('.ui.dropdown').dropdown();

function req(data) {
    $.ajax({
        type: 'POST',
        url: $('#ajax-url').val(),
        data,
        headers: {
            'X-CSRFToken': $('#csrf-token').val(),
        },
        success: () => window.location.reload()
    });
}

function showEditDialog(event) {
    const q = $(event.target).parents('tr');
    $('#dialog-username').text(q.data('username'));
    $('.ui.modal').modal('show');
    $('input[name="id"]').val(q.data('userid'));
    $('input[name="username"]').val(q.data('username'));
    $('#dropdown-role').dropdown('set selected', q.data('role'));
    $('#dropdown-facility').dropdown('set selected', q.data('facility'));
}

function deleteUser(event) {
    $(event.target).addClass('disabled').addClass('loading');
    const id = $(event.target).parents('tr').data('userid');
    req({ type: 'delete', id });
}

function toggleBan(event) {
    $(event.target).addClass('disabled').addClass('loading');
    const id = $(event.target).parents('tr').data('userid');
    req({ type: 'ban', id });
}