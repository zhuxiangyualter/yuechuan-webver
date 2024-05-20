
const font_sizes = {
    "normal": "1.0em",
    "small": "0.75em",
    "large": "1.5em",
    "huge": "2.5em"
};

class MessageSegment {
    constructor(type = 'none', data = {}) {
        this.type = type;
        this.data = data;
    }

    static text(text, attr) {
        return new MessageSegment('text', { text, attr });
    }

    static image(data) {
        return new MessageSegment('image', data);
    }
}

class Message {
    #sender = {};
    #message = [];
    #time = undefined;

    static parse(s) {
        s = JSON.parse(s);
        const { message, sender, time } = s;
        const result = new Message();
        result.#sender = sender;
        result.#message = message;
        result.#time = time;
        return result;
    }

    set_sender({ username, avatar, role, facility }) {
        this.#sender = { username, avatar, role, facility };
    }

    insert_text(text, attr) {
        this.#message.push(MessageSegment.text(text, attr));
    }

    insert_image(data) {
        this.#message.push(MessageSegment.image({ src: data }));
    }

    serialize() {
        return JSON.stringify({
            message: this.#message,
            sender: this.#sender
        });
    }

    commit(container) {
        const result = $('<div class="event" />');
        const msg = $('<div />');
        for (const { type, data } of this.#message) {
            let node;

            if (type == 'text') {
                node = $('<span />').text(data.text);
                node.appendTo(msg);
                if (data.attr) {
                    if (data.attr.bold) {
                        node.wrap('<b />');
                    }
                    if (data.attr.underline) {
                        node.wrap('<u />');
                    }
                    if (data.attr.italic) {
                        node.wrap('<i />');
                    }
                    if (data.attr.link) {
                        node.wrap(`<a href="${data.attr.link}" />`);
                    }
                    if (data.attr.strike) {
                        node.wrap('<s />');
                    }
                    if (data.attr.size) {
                        node.css('font-size', font_sizes[data.attr.size]);
                    }
                }
            }
            else if (type == 'image') {
                node = $('<img />').attr('src', data.src);
                node.appendTo(msg);
            }
        }

        if (this.#sender) {
            $(`
                <div class="label">
                    <img src="${this.#sender.avatar}">
                </div>
                <div class="content">
                    <div class="summary">
                        <b>${this.#sender.username}</b>
                    </div>
                    <div class="extra text">
                    </div>
                    <div class="meta">
                        ${this.#time ? new Date(this.#time).toTimeString().split(' ')[0] : '未知时间'}
                    </div>
                </div>`).appendTo(result);
            msg.appendTo(result.find('.extra.text'));
        }

        result.appendTo($(container));
    }
}