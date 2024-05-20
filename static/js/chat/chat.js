if (location.port) path = `${location.hostname}:${location.port}/`;
else path = `${location.hostname}/`;

var socket = new WebSocket(`ws://${path}${$('#input-facility').val()}/`);

socket.onopen = function (event) {
    $('.dimmer').removeClass('active');
    $('.loader').removeClass('active');
}

socket.onmessage = function ({ data: sdata }) {
    const data = JSON.parse(sdata);
    if (data.type == 'info') {
        // ..
    }
    else if (data.type == 'message') {
        Message.parse(data.data).commit('#message-container');
    }
}

socket.onclose = function (event) {
    $('.dimmer').addClass('active');
    $('.loader').text('连接断开');
}

var quill = new Quill('.editor', {
    modules: {
        toolbar: {
            container: '#quill-toolbar'
        }
    },
    theme: 'snow',
    placeholder: '输入内容...'
});

function send() {
    const delta = quill.getContents();
    if (delta.ops.length == 1 && delta.ops[0].insert.trim().length == 0) {
        return;
    }


    const msg = new Message();

    msg.set_sender({
        username: $('#input-username').val(),
        avatar: $('#input-avatar').val(),
        role: $('#input-role').val(),
    });

    for (op of delta.ops) {
        if (typeof op.insert == 'string') {
            msg.insert_text(op.insert, op.attributes);
        }
        else if (op.insert.image) {
            msg.insert_image(op.insert.image);
        }
    }
    socket.send(msg.serialize());

    quill.deleteText(0, quill.getLength());
}

$('.editor').keydown(e => {
    if (e.key == 'Enter' && e.ctrlKey) {
        $('#button-send').click();
    }
});