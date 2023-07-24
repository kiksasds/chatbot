//cria e seta input
function ci(){
	let i = document.createElement("input");
	i.type = "text";
	return i;
}

//cria e seta botao
function cb(){
	b = document.createElement("button");
	b.type = "button";
	return b;
}

//cria e seta header
function ch(t) {
    h = document.createElement("header");
    h.textContent = t;
    return h;
}

//adiciona input a div
function ai(d, is, b){
	is.push(ci());
	d.insertBefore(is[is.length - 1], b);
	d.insertBefore(document.createElement("br"), b);
}

//cria e seta formulario
f = document.getElementsByTagName("form")[0];

//campos input para recuperar valores
it = ci();
ht = ch("Tag:");
f.appendChild(ht);
f.appendChild(it);

dq = document.createElement("div");
hq = ch("Perguntas:");
f.appendChild(hq);
f.appendChild(dq);
iqs = [];
bq = cb();
bq.innerText = "Nova Pergunta";
dq.appendChild(bq);
bq.onclick = () =>{ai(dq, iqs, bq);}

da = document.createElement("div");
ha = ch("Respostas:");
f.appendChild(ha);
f.appendChild(da);
ias = [];
ba = cb();
ba.innerText = "Nova Resposta";
da.appendChild(ba);
ba.onclick = () =>{ai(da, ias, ba);}

bs = cb();
bs.innerText = "Enviar";
f.appendChild(bs);
bs.onclick = () => {
	d = new Object();
	d.tag = it.value;
	d.patterns = [];
	iqs.forEach((v) => {if(v.value != "") d.patterns.push(v.value)});
	d.responses = [];
	ias.forEach((v) => {if(v.value != "") d.responses.push(v.value)});

    if((d.tag == "") || (d.patterns == []) || (d.responses == [])){
        if(d.tag == "") ht.innerText = "Em branco Tag:";
        if(d.patterns == []) hq.innerText = "Em branco Perguntas:";
        if(d.responses == []) ha.innerText = "Em branco Respostas:";
    }
	console.log(JSON.stringify(d));

	fetch('http://127.0.0.1:5000/form', {
		method: 'POST',
		body: JSON.stringify({ message: d }),
		mode: 'cors',
		headers: {
		  'Content-Type': 'application/json'
		}
	})
	.catch((error) => {
		console.error('Error:', error);
	});
}