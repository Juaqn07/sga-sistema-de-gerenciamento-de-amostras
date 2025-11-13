<?php
if(isset($_POST['btn-atualizar'])):
	$nome=filter_var($_POST['nome'],FILTER_SANITIZE_STRING);
	$sobrenome=filter_var($_POST['sobrenome'],FILTER_SANITIZE_STRING);
	$email=filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
	$idade=filter_var($_POST['idade'],FILTER_SANITIZE_NUMBER_INT);
	$id=filter_var($_POST['id'], FILTER_SANITIZE_NUMBER_INT);
	

	//Conexão
	require_once 'banco.php';

	$sql="UPDATE clientes SET nome='$nome', sobrenome='$sobrenome', email='$email', idade=$idade WHERE  id=$id";
	echo $sql;
	if(mysqli_query($connect,$sql)):		
		header('Location: consultar.php?atualiza=ok');
	else:		
		header('Location: consultar.php?atualiza=erro');
	endif;
endif;	

?>