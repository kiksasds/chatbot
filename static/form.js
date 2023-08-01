//cria e seta input
function ci(){
	let i = document.createElement("input");
	i.type = "text";
	return i;
}

//cria e seta botao
function cb(t){
	b = document.createElement("button");
	b.type = "button";
	b.innerText = t;
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
ht = ch("Tag:");
it = ci();
bt = cb("Pesquisar");
f.appendChild(ht);
f.appendChild(it);
f.appendChild(bt);
bt.onclick = () =>{
    fetch('http://127.0.0.1:5000/form?tag='+it.value, {
		method: 'GET',
		mode: 'cors'
	})
	.then(r => r.json())
	.then(r => {
	    it.value = r['tag'];
	    for (i in r['patterns']){
	        ai(dq, iqs, bq);
	        iqs[iqs.length-1].value = r['patterns'][i];
	    }
	    for (i in r['responses']){
	        ai(da, ias, ba);
	        ias[ias.length-1].value = r['responses'][i];
	    }
	})
	.catch((error) => {
		console.error('Error:', error);
	});
}

dq = document.createElement("div");
hq = ch("Perguntas:");
f.appendChild(hq);
f.appendChild(dq);
iqs = [];
bq = cb("Nova Pergunta");
dq.appendChild(bq);
bq.onclick = () =>{ai(dq, iqs, bq);}

da = document.createElement("div");
ha = ch("Respostas:");
f.appendChild(ha);
f.appendChild(da);
ias = [];
ba = cb("Nova Resposta");
da.appendChild(ba);
ba.onclick = () =>{ai(da, ias, ba);}

bs = cb("Enviar");
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