<?php include_once 'header.php';?>

<div class="row">
	<div class="container my-3">               
	 <!--(2) Exemplo de formulario-->
	 <h1 class="display-3 mx-3 ">Novo Cliente</h1>
	 <form action="incluir.php" method="POST">
		 <div class="row mx-3 g-2">
			 <div class="col-2">
				 <!--(3) adicionar o atributo required ao campo text-->
				 <label for="nome" class="form-label">Nome</label>
				 <input type="text" class="form-control" id="nome" name="nome" required>
			 </div>
			 <div class="col-4">
				 <label for="sobrenome" class="form-label">Sobrenome</label>
				 <input type="text" class="form-control" id="sobrenome" name="sobrenome">
			 </div>
			
			 <div class="col-9">
			 	<div class="col-5">
				 <label for="email" class="form-label">Email</label>
				 <input type="text" class="form-control" id="email" name="email">
				</div>
			 </div>
			 <div class="col-4">
			 	<div class="col-2">
				 <label for="idade" class="form-label">Idade</label>
				 <input type="number" class="form-control" id="idade" name="idade" min="10" max="120">
				</div>
			 </div>
			 
		 </div>
		 <div class="row mx-3 my-3 g-2">
		 	<div class="col-2">
				<button type="submit" name="btn-cadastrar" class="btn btn-primary"> Cadastrar</button>
				<a href="consultar.php" type="submit" name="btn-cadastrar" class="btn btn-primary"> Lista de clientes</a>
			</div>
		</div>
	 </form>    
 </div>
<?php include_once 'footer.php';?>
