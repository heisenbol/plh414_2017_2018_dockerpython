<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
	<title>Login on SKAUTH2</title>
	<style>
		div.head p, .footer p {
			font-size: 160%;
			font-weight: bold;
			border: 1px solid #d6d4d4;
			background-color: #f7f5f5;
			padding: 0.3em;
		}
		.specialtype {
			font-size:80%;
		}
		div.menu ul {
			margin:0;
			padding:0;
			list-style:none;
		}
		div.menu ul li {
			display: inline-block;
			margin-right:1em;
		}
		div.menu ul li:last-child {
			
			margin-right:0;
		}
		
		div.content {
			width:50%;
			margin-left:auto;
			margin-right:auto;
			border: 1px solid #d6d4d4;
			padding:1em;
		}
		div.flash {
			background-color:yellow;
			border:2px solid red;
			padding:1em;
			color:red;
		}
		select, input {
			padding:0.3em;
		}
	</style>
</head>
<body>
	% include('head.tpl')
	% include('menu.tpl')

	<div class="content">	
		<h1>Super System Login1</h1>
		<h2>Super System Login2</h2>
		<p>Please enter your credentials1</p>
		<p class="specialtype">Please enter your credentials2</p>
		 % if flash!='':
				<div class="flash">
				{{flash}}
				</div>
		 % end


		<form action="dologin" method="POST">


		 % if callback!='':
 			<input type="hidden" name="callback" value="{{callback}}">
		 % end
			<p>
				<label>Σύστημα
					%if system!=False and system!="" and systemExists != False:
							<input type="hidden" name="system" value="{{system}}">
							{{system}}
					%else :
							<select name='system'>
									%for aSystem in allSystems:
										<option value="{{aSystem['identifier]}}">{{aSystem['identifier']}}</option>
									%end
								<option value='INVALID'>INVALID - Some other system</option>
							</select>
					%end

				</label>
				
				<br><label>Όνομα χρήστη <input name="username" type="text" ></label>
				<br><label>Κωδικός πρόσβασης <input name="password" type="password"></label>
				<br><label>Redirect METHOD <select name="redirectmethod"><option value="GET">GET</option><option value="POST">POST</option><option value="NONE">NONE</option></select></label>
			</p>
			<p><input type="submit" value="Login" ></p>
		</form>
	</div>
	
	<div class="footer">
		<p>&copy; 2018</p>
	</div>
</body>
</html>
