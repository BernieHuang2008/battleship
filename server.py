import random
import socket
import webview

# 创建socket
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 本地信息
address = ('', 3001)

# 绑定
tcp_server_socket.bind(address)

# 使用socket创建的套接字默认的属性是主动的，
# 使用listen将其变为被动的，这样就可以接收别人的链接了
tcp_server_socket.listen(128)

# 如果有新的客户端来链接服务器，
# 那么就产生一个新的套接字专门为这个客户端服务
# client_socket用来为这个客户端服务
# tcp_server_socket就可以省下来专门等待其他新客户端的链接
print("Serving on", socket.gethostbyname(socket.gethostname()))
print("Waiting for TCP connection ...")
client_socket, clientAddr = tcp_server_socket.accept()
print("Connected to '{}'".format(': '.join(map(str, clientAddr))))


# 接收对方发送过来的数据
def send(message):
    print("send:", message)
    client_socket.send(message.encode("utf-8"))
    msg = client_socket.recv(1024)
    print("recv:", msg.decode('utf-8'))
    return msg.decode("utf-8")


# 接收对方发送过来的数据
def recv(require_response):
    recv_data = client_socket.recv(1024)  # 接收1024个字节
    print("recv:", recv_data.decode('utf-8'))
    resp = require_response(recv_data.decode('utf-8'))
    print("send:", resp)
    client_socket.send(resp.encode('utf-8'))


my_boats = []


def next_step(s):
    s = s.split('/')
    if s[0] == 'attack':
        window.evaluate_js("setTimeout('init(1,1)', 100)")
        coord = s[1] + ',' + s[2]
        window.evaluate_js("attack(" + coord + ")")
        if coord not in my_boats:
            return 'res/empty'
        else:
            window.evaluate_js("boat_dead(" + coord + ")")
            my_boats.remove(coord)
            if len(my_boats) == 0:
                window.evaluate_js(
                    "function win(){alert('You lost all the boats!');pywebview.api.exterminate();};setTimeout(win, 10)")
                return "game/over"
            return 'res/dead'
    elif s[0] == "promise":
        message = """
        =====Promise=====
        
        I promise you, 
        {}
        
        =================
        Promise Steps: {}.
        """.format(s[1], s[2].replace('\n', '\n\t\t'))
        if window.evaluate_js("confirm(`" + message + "`)"):
            window.evaluate_js("setTimeout('pywebview.api.evaluate(\"recv(next_step)\")', 10)")
            return "promise/accept"
        else:
            window.evaluate_js("setTimeout('pywebview.api.evaluate(\"recv(next_step)\")', 10)")
            return "promise/denied"


def set_boat():
    window.evaluate_js("set_boat()")


def logic(win):
    global my_boats
    while not(len(my_boats) == 3 and all(all(1 <= y <= 10 for y in map(int, x.split(','))) for x in my_boats)):
        my_boats = window.evaluate_js("prompt('Boat Positions: ')").split(' ')
    with open("server log.sys", 'w') as f:
        f.write(str(my_boats))
    who_first = "Server" if random.random() > 0.5 else "Client"
    resp = send("init/first/" + who_first)
    if resp == "sys/ok":
        pass
    else:
        window.evaluate_js("alert('Response Error!')")
        exit(0)
    if who_first == "Server":
        window.evaluate_js("init(1)")
    else:
        window.evaluate_js("init(0)")
        recv(next_step)


class api:
    def __init__(self):
        pass

    def hey(self, msg):
        resp = send(msg)
        return resp

    def recv_next(self):
        recv(next_step)

    def sb_recall(self, boats):
        global my_boats
        my_boats = boats.copy()

    def evaluate(self, script):
        eval(script)

    def exterminate(self):
        window.destroy()
        exit(0)

    def promise(self, a, b):
        if send("promise/{}/{}".format(a, b)) == "promise/accept":
            return True
        return False


window = webview.create_window('Server', js_api=api(), html="""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <style>
            td {
                width: 30px;
                height: 30px;
                text-align: center;
                border: solid 1px black;
                font-size: 30px;
                line-height: 0px;
            }

            body {
                display: flex;
                /* justify-content: center; */
                align-items: center;
                margin: 0;
                height: 100vh;
            }

            .header {
                background-color: black;
                color: white;
                font-size: 17px !important;
            }

            .symbol {
                position: absolute;
            }

            .blue {
                color: #9cdcfe;
            }

            .gray {
                color: gray;
            }

            .green {
                color: green;
            }
        </style>
        <table id="t" style="display: block;" cellspacing="1px">
            <tbody>
                <tr></tr>
            </tbody>
        </table>
        <div id="mb">Message from System</div>
        <script>
            var t = document.getElementById('t');
            var mb = document.getElementById('mb');
            var promised_turn = 0;
            for (var i = 0; i <= 10; i++) {
                t.children[0].children[0].innerHTML += `<td class='header'>${i}</td>`;
            }
            for (var i = 0; i < 10; i++) {
                s = '';
                for (var j = 0; j <= 10; j++) {
                    if (j)
                        s += `<td onclick="clicked(${i+1}, ${j})"></td>`;
                    else
                        s += `<td class='header'>${String.fromCharCode('A'.charCodeAt()+i)}</td>`;
                }
                t.children[0].innerHTML += `<tr>${s}</tr>`;
            }

            function attack(x, y) {
                t.children[0].children[x].children[y].style.backgroundColor = "rgba(255, 192, 203, 0.5)";
            }

            function empty(x, y) {
                t.children[0].children[x].children[y].innerHTML += "<div class='symbol'>X</div>";
            }

            function place_boat(x, y) {
                t.children[0].children[x].children[y].innerHTML += "<div class='symbol blue'>O</div>";
            }

            function boat_dead(x, y) {
                t.children[0].children[x].children[y].innerHTML += "<div class='symbol gray'>O</div>";
            }

            function boat_found(x, y) {
                t.children[0].children[x].children[y].innerHTML += "<div class='symbol green'>√</div>";
            }

            var turn = -1;

            function init(tu, esc) {
                turn = tu;
                if (turn == 1) {
                    mb.innerText = "Your Turn!";
                }
                if (turn == 0) {
                    mb.innerText = "The Other's Turn.";
                }
                if (turn == -1) {
                    mb.innerText = "Game not Started yet.";
                }
                if (promised_turn > 0 && esc == 1){
                    promised_turn--;
                    clicked(0, 0);
                    return;
                }
            }
            init(-1);
            var pb=-1;
            var pbs=[];
            
            async function clicked(x, y) {
                if (pb>0){
                    pb--;
                    pbs.push(`${x},${y}`);
                    place_boat(x, y);
                }
                if (pb==0){
                    pb--;
                    pywebview.api.sb_recall(pbs);
                }
                if (turn == 1) {
                    init(0);
                    var message = `attack/${x}/${y}`;
                    var hey_res = await hey(message);
                    if (hey_res == "res/empty")
                        empty(x, y);
                    else if (hey_res == "res/dead")
                        boat_found(x, y);
                    else if (hey_res == "game/over"){
                        alert("You win the game!");
                        pywebview.api.exterminate();
                    }
                }
            }

            async function hey(message) {
                var r;
                await pywebview.api.hey(message).then(res=>{r=res});
                pywebview.api.recv_next();
                return r;
            }
            
            async function promise(){
                if(turn==1){
                    var a = prompt("Promise: ");
                    var b = Number(prompt("Cost steps: "));
                    await pywebview.api.promise(a, b).then(res=>{
                        if(res){
                            alert("Promise accepted by the other player.");
                            promised_turn = b-1;
                            clicked(0, 0);
                        }
                        else{
                            alert("Promise denied by the other player.");
                            promised_turn = 0;
                        }
                    });
                }
            }
            document.addEventListener('keydown', async function(e){
                if(e.key == 'p')
                    await promise();
            });
            
            function set_boat(){
                mb.innerText = "Select THREE Different Squares to place your boat.";
                pb=3;
            }
        </script>
    </body>
</html>

""")

webview.start(logic, window, gui='edgechromium')

client_socket.close()
