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

//adiciona input a div
function ai(d, is, b){
	is.push(ci());
	d.insertBefore(is[is.length - 1], b);
	d.insertBefore(document.createElement("br"), b);
}

//cria e seta formulario
//f = document.createElement("form");
//document.body.appendChild(f);
f = document.getElementsByTagName("form")[0];

//campos input para recuperar valores
it = ci();
f.appendChild(it);

dq = document.createElement("div");
f.appendChild(dq);
iqs = [];
bq = cb();
bq.innerText = "Nova Questão";
dq.appendChild(bq);
bq.onclick = () =>{ai(dq, iqs, bq);}

da = document.createElement("div");
f.appendChild(da);
ias = [];
ba = cb();
ba.innerText = "Nova Respota";
da.appendChild(ba);
ba.onclick = () =>{ai(da, ias, ba);}

bs = cb();
bs.innerText = "Enviar";
f.appendChild(bs);
bs.onclick = () => {
	d = new Object();
	d.tag = it.value;
	d.patterns = [];
	iqs.forEach((v) => {d.patterns.push(v.value)});
	d.responses = [];
	ias.forEach((v) => {d.responses.push(v.value)});

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