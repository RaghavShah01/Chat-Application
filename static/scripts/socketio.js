document.addEventListener('DOMContentLoaded', ()=>{
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    const username = document.querySelector('#get-username').innerHTML;

    let room="lounge";
    joinRoom("lounge");


    // diplay messages
    socket.on('message', data =>{
        if(data.msg){
        const p = document. createElement('p');
        const span_username = document. createElement('span');
        const span_timestamp = document. createElement('span');
        const br = document.createElement('br');
            // Display user's own message
            if (data.username == username) {
                    p.setAttribute("class", "my-msg");

                    // Username
                    span_username.setAttribute("class", "my-username");
                    span_username.innerText = data.username;

                    // Timestamp
                    span_timestamp.setAttribute("class", "timestamp");
                    span_timestamp.innerText = data.time_stamp;

                    // HTML to append
                    p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML

                    //Append
                    document.querySelector('#display-message-section').append(p);
            } // Display other users' messages
            else if (typeof data.username !== 'undefined') {
                p.setAttribute("class", "others-msg");

                // Username
                span_username.setAttribute("class", "other-username");
                span_username.innerText = data.username;

                // Timestamp
                span_timestamp.setAttribute("class", "timestamp");
                span_timestamp.innerText = data.time_stamp;

                // HTML to append
                p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;

                //Append
                document.querySelector('#display-message-section').append(p);
            }
            // Display system message
            else {
                printSysMsg(data.msg);
            }


        }
        scrollDownChatWindow();
    });

    // send message
    document.querySelector('#send_message').onclick = ()=>{
        socket.send({'msg': document.querySelector('#user_message').value,'username':username,'room': room});
        // Clear input area
        document.querySelector('#user_message').value='';
    }

    // Room selection
    document.querySelectorAll('.select-room').forEach(p =>{
        p.onclick= () => {
            let newRoom = p.innerHTML;
            if(newRoom == room){
                msg = `you are already in ${room} room.`
                printSysMsg(msg);
            }
            else{
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        }
    });


        // Logout from chat
        document.querySelector("#logout-btn").onclick = () => {
            leaveRoom(room);
        };

    // leave Room
    function leaveRoom(room){
        socket.emit('leave',{'username':username, 'room':room});
    }

    // Join Room
    function joinRoom(room){
        socket.emit('join',{'username':username, 'room':room});
        // clear message section
        document.querySelector('#display-message-section').innerHTML = ''
        // Autofocus on text box
        document.querySelector('#user_message').focus();
    }

        // Scroll chat window down
        function scrollDownChatWindow() {
            const chatWindow = document.querySelector("#display-message-section");
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

    // print system message
    function printSysMsg(msg){
        const p = document.createElement('p');
        p.innerHTML = msg;
        document.querySelector('#display-message-section').append(p);
    }
})