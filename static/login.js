document.addEventListener('DOMContentLoaded', function() {
    const entrar = document.querySelector('#entrar');
    const inscrever = document.querySelector('#inscrever');
    const loginForm = document.querySelector('.login form');
    const cadastroForm = document.createElement('form');
    cadastroForm.action = '/cadastro';
    cadastroForm.method = 'POST';
    cadastroForm.innerHTML = `<input type="text" class="text" id="username" name="username" placeholder="Nome de Usuário" required>
        <br><br>
        <input type="text" class="text" id="registration" name="registration" placeholder="Matrícula" required>
        <br><br>
        <input type="password" class="text" id="password" name="password" placeholder="Senha" required>
        <br><br>
        <input type="checkbox" id="tutor" name="tutor">
        <label for="tutor">Sou um tutor</label>
        <br><br>
        <button class="signin" type="submit">Cadastrar</button>`;
    cadastroForm.style.display = 'none';
    loginForm.parentNode.insertBefore(cadastroForm, loginForm.nextSibling);

    entrar.addEventListener('click', function() {
        entrar.classList.add('active');
        entrar.classList.remove('nonactive');
        inscrever.classList.add('nonactive');
        inscrever.classList.remove('active');
        loginForm.style.display = 'block';
        cadastroForm.style.display = 'none';
    });

    inscrever.addEventListener('click', function() {
        inscrever.classList.add('active');
        inscrever.classList.remove('nonactive');
        entrar.classList.add('nonactive');
        entrar.classList.remove('active');
        loginForm.style.display = 'none';
        cadastroForm.style.display = 'block';
    });
});
