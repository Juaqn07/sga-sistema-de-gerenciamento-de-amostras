<?php
//Header
include_once 'header.php';

//Select com o id que veio da URL
if(isset($_GET['id'])):
	
	//Conexão
	include_once 'banco.php';
	$id =filter_var($_GET['id'],FILTER_SANITIZE_STRING);
	
	$sql="SELECT * FROM clientes WHERE id =  '$id'";
	$resultado = mysqli_query($connect, $sql);
	$dados = mysqli_fetch_array($resultado);
endif;
 
 ?>

<div class="row">
<div class="container my-3">
	
		<form action="atualizar.php" method="POST">

		<div class="row mx-3 g-2">
			<h1 class="display-5 mx-3 ">Atualizar Cliente</h1>
			<input type="hidden" name="id" value="<?php echo $dados['id']; ?>">
			<div class="input-field col s1">
				<label for="nome"> Nome</label>
				<input type="text" name="nome" id="nome" value="<?php echo $dados['nome']; ?>">
				
			</div>
		
			<div class="input-field col s1">
				<label for="sobrenome"> Sobrenome</label>
				<input type="text" name="sobrenome" id="sobrenome" value="<?php echo $dados['sobrenome']; ?>">
				
			</div>
			
			<div class="input-field col s1">
				<label for="email"> Email</label>
				<input type="text" name="email" id="email" value="<?php echo $dados['email']; ?>" >
				
			</div>
				
			<div class="input-field col s1">
				<label for="idade"> Idade</label>
				<input type="number" name="idade" id="idade" min="10" max="120" value="<?php echo $dados['idade']; ?>">
				
			</div>

			<div class="input-field col s1">
				
			</div>
			
			<div class="row mx-3 my-3 g-2">
				<div class="col-2">
					<button type="submit" name="btn-atualizar"  class="btn btn-primary">Atualizar</button>
					<a href="consultar.php" type="submit" class="btn btn-primary">Lista de clientes</a>
					
				</div>
			</div>
		</div>
		</form>
		
	</div>
</div>


<?php include_once 'footer.php';?>

     
 
