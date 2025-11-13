<?php
//Iniciar  Sessão
session_start();

if(isset($_POST['btn-cadastrar'])):
	//Tranforma caracteres especiais em HTML
	$nome=filter_input(INPUT_POST,'nome',FILTER_SANITIZE_SPECIAL_CHARS);
	//Tranforma caracteres especiais em HTML
	$sobrenome=filter_input(INPUT_POST,'sobrenome',FILTER_SANITIZE_SPECIAL_CHARS);
	//Remove todos caracteres, exceto letras, números e !#$%&'*+-=?^_`{|}~@.[].
	$email = filter_input(INPUT_POST,'email',FILTER_SANITIZE_EMAIL);
	//Remove todos caracteres, exceto números sinal de mais e menos.
	$idade = filter_input(INPUT_POST,'idade',FILTER_SANITIZE_NUMBER_INT);

	//Conexão
	require_once 'banco.php';

	
	$sql="INSERT INTO clientes(nome,sobrenome,email,idade) VALUES ('$nome', '$sobrenome', '$email', $idade)";
	echo $sql;
	if(mysqli_query($connect,$sql)):
		$_SESSION['mensagem'] = "Cadastro com sucesso!";
		header('Location: consultar.php?sucesso');
	else:
		$_SESSION['mensagem'] = "Erro ao cadastrar!";		
		header('Location: consultar.php?erro');
	endif;
endif;	

?>